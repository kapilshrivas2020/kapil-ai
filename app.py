from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
import os

load_dotenv(override=True)

MODEL_NAME = "gemini-3.1-flash-lite"

# grok_api_key = os.getenv('GROK_API_KEY')
# GROK_BASE_URL = "https://api.x.ai/v1"
# grok = OpenAI(api_key=grok_api_key, base_url=GROK_BASE_URL)

# groq_api_key = os.getenv('GROQ_API_KEY')
# GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# groq = OpenAI(api_key=groq_api_key, base_url=GROQ_BASE_URL)

# openai = OpenAI()
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
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


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Kapil Twin AI",
        description="Talk to my AI twin about me",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
