import json
import os
# import requests
from dotenv import load_dotenv

load_dotenv(override=True)

# pushover_user = os.getenv("PUSHOVER_USER")
# pushover_token = os.getenv("PUSHOVER_TOKEN")

# pushover_url = "https://api.pushover.net/1/messages.json"


# def push(text):
#     requests.post(
#         pushover_url,
#         data={
#             "token": pushover_token,
#             "user": pushover_user,
#             "message": text,
#         },
#     )



def pushQuestions(message):
    print(f"Message pushed to record : {message}")
    with open("qa_details.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    return "Message received"

def pushDetails(message):
    print(f"Message pushed to record : {message}")
    with open("user_details.txt", "a", encoding="utf-8") as f:
        f.write(message + "\n")
    return "Message received"


# def record_user_details(email, name="Name not provided", notes="not provided"):
#     push(f"Recording interest from {name} with email {email} and notes {notes}")
#     return "OK"

def record_user_details(email="test@test.com", contact="1234567890", notes="not provided"):
    pushDetails(f"Recording interest email {email}, contact {contact}, and notes {notes}")
    return {"recorded": "ok"}

def record_user_name(name):
    pushDetails(f"Recording interest from {name}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    pushQuestions(f"Recording {question} asked")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record user who is interested in being in touch and provided an email address or contact",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "contact":{
                "type": "string",
                "description": "The contact number of this user"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": [],
        "additionalProperties": False
    }
}

record_user_name_json = {
    "name": "record_user_name",
    "description": "Always use this tool to record user name",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of this user"
            },
        },
        "required": ["name"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question particular on my love life, relationship, girlfriends and habits",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The questions"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json},
        {"type": "function", "function": record_user_name_json}]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
    "record_user_name": record_user_name
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "Unknown tool: " + tool_name
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results
