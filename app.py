from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls
from styles import CSS, JS, EXAMPLES, GOLD
from dotenv import load_dotenv
import gradio as gr
import os

load_dotenv(override=True)

for _key in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
    if os.environ.get(_key) is not None:
        os.environ[_key] = os.environ[_key].strip()


def _api_key() -> str:
    return (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()


MODEL_NAME = "gemini-3.1-flash-lite"

# grok_api_key = os.getenv('GROK_API_KEY')
# GROK_BASE_URL = "https://api.x.ai/v1"
# grok = OpenAI(api_key=grok_api_key, base_url=GROK_BASE_URL)

# groq_api_key = os.getenv('GROQ_API_KEY')
# GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# groq = OpenAI(api_key=groq_api_key, base_url=GROQ_BASE_URL)

# openai = OpenAI()
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = _api_key()
if not google_api_key:
    raise RuntimeError(
        "Missing GOOGLE_API_KEY. Add it to your Streamlit app secrets "
        "(Settings → Secrets) or as an environment variable."
    )
gemini = OpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def chat(message, history):
    messages = system + history + [{"role": "user", "content": message}]
    response = gemini.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = gemini.chat.completions.create(model=MODEL_NAME, messages=messages, tools=tools)
    return response.choices[0].message.content


def _is_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


def run_streamlit():
    import streamlit as st

    st.set_page_config(page_title="Kapil Twin AI", page_icon="🤖", layout="centered")
    st.markdown(
        f"""
        <style>
        .stApp {{ background: #0d0d10; color: #ececef; }}
        h1 {{ border-left: 3px solid {GOLD}; padding-left: 12px; }}
        .stChatMessage {{ background: #16161b; border: 1px solid #2a2a32; }}
        div[data-testid="stChatMessageContent"] {{ color: #ececef; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Kapil Twin AI")
    st.caption("Talk to my AI twin about me")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    cols = st.columns(2)
    for index, example in enumerate(EXAMPLES):
        if cols[index % 2].button(example, use_container_width=True, key=f"example_{index}"):
            st.session_state.pending_prompt = example

    prompt = st.chat_input("Ask me anything...")
    user_message = prompt or st.session_state.pop("pending_prompt", None)
    if user_message:
        with st.spinner("Thinking..."):
            reply = chat(user_message, st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": user_message})
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def run_gradio():
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Kapil Twin AI",
        description="Talk to my AI twin about me",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())


if _is_streamlit():
    run_streamlit()
elif __name__ == "__main__":
    run_gradio()
