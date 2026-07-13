import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

_docs_service = None

def _append_via_apps_script(webhook_env_key: str, message: str) -> None:
    webhook_url = os.getenv(webhook_env_key)
    if not webhook_url:
        raise RuntimeError(f"Missing {webhook_env_key}")

    payload = {"message": message}
    secret = os.getenv("GOOGLE_APPS_SCRIPT_SECRET")
    if secret:
        payload["secret"] = secret

    response = requests.post(webhook_url, json=payload, timeout=30)
    response.raise_for_status()
    print(f"message written successfuly : {response}")


def _append_message(doc_env_key: str, webhook_env_key: str, message: str) -> None:
    if os.getenv(webhook_env_key):
        _append_via_apps_script(webhook_env_key, message)
    else:
        print("Not able to push message")


def pushQuestions(message):
    print(f"Message pushed to record : {message}", flush=True)
    try:
        _append_message("GOOGLE_QA_DOC_ID", "GOOGLE_QA_WEBHOOK_URL", message)
    except Exception as exc:
        print(f"Failed to write to Google Doc: {exc}", flush=True)
    return "Message received"


def pushDetails(message):
    print(f"Message pushed to record : {message}", flush=True)
    try:
        _append_message("GOOGLE_USER_DETAILS_DOC_ID", "GOOGLE_USER_DETAILS_WEBHOOK_URL", message)
    except Exception as exc:
        print(f"Failed to write to Google Doc: {exc}", flush=True)
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
