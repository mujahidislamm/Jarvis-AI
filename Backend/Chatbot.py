from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError(
        "GroqAPIKey was not found in your .env file."
    )


# ============================================================
# INITIALIZE GROQ CLIENT
# ============================================================

client = Groq(api_key=GroqAPIKey)


# ============================================================
# SETTINGS
# ============================================================

MAX_MESSAGES = 3

MODEL = "qwen/qwen3.8-27b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

System = f"""
You are {Assistantname}, an advanced AI assistant.

User: {Username}

Rules:
- Reply in English only.
- Be helpful and accurate.
- Keep responses concise and relevant.
- Use proper grammar and punctuation.
- Do not mention your training data unless specifically asked.
- Do not provide unnecessary notes or explanations.
"""


# ============================================================
# CHAT LOG
# ============================================================

SystemChatBot = [
    {
        "role": "system",
        "content": System
    }
]


chat_log_path = os.path.join(PROJECT_ROOT, "Data", "ChatLog.json")

os.makedirs(
    os.path.dirname(chat_log_path),
    exist_ok=True
)


# ============================================================
# LOAD PREVIOUS CHAT HISTORY
# ============================================================

try:

    with open(chat_log_path, "r", encoding="utf-8") as f:
        messages = load(f)

    if not isinstance(messages, list):
        messages = []

except (FileNotFoundError, ValueError):

    messages = []


# ============================================================
# REAL-TIME INFORMATION
# ============================================================

def RealtimeInformation():

    current_date_time = datetime.datetime.now()

    return (
        f"Current date and time:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d %B %Y')}\n"
        f"Time: {current_date_time.strftime('%H:%M:%S')}"
    )


# ============================================================
# ANSWER MODIFIER
# ============================================================

def AnswerModifier(answer):

    lines = answer.split("\n")

    non_empty_lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    return "\n".join(non_empty_lines)


# ============================================================
# CHATBOT
# ============================================================

def ChatBot(Query):

    global messages

    try:

        # Add user's message
        messages.append(
            {
                "role": "user",
                "content": Query
            }
        )

        # Keep chat history within limit
        if len(messages) > MAX_MESSAGES:
            messages = messages[-MAX_MESSAGES:]


        # Prepare messages
        chat_messages = (
            SystemChatBot
            + [
                {
                    "role": "system",
                    "content": RealtimeInformation()
                }
            ]
            + messages
        )


        # Send request to Groq
        completion = client.chat.completions.create(

            model=MODEL,

            messages=chat_messages,

            max_tokens=1024,

            temperature=0.5,

            top_p=0.9,

            stream=False
        )


        # Collect response
        Answer = completion.choices[0].message.content or ""
        if not Answer and getattr(completion.choices[0].message, "reasoning", None):
            Answer = completion.choices[0].message.reasoning


        # Clean response
        Answer = Answer.strip()
        Answer = Answer.replace("</s>", "")


        # Save assistant response
        messages.append(
            {
                "role": "assistant",
                "content": Answer
            }
        )


        # Save chat history
        with open(
            chat_log_path,
            "w",
            encoding="utf-8"
        ) as f:

            dump(
                messages,
                f,
                indent=4,
                ensure_ascii=False
            )


        return AnswerModifier(Answer)


    except Exception as e:

        print(f"\nError: {e}\n")

        return (
            "Sorry, there was an issue "
            "processing your request. "
            "Please try again."
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        f"{Assistantname} is ready."
    )

    print(
        "Type 'exit', 'quit', or 'bye' to stop.\n"
    )


    while True:

        user_input = input(
            "ENTER YOUR QUESTION: "
        ).strip()


        if not user_input:
            continue


        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print("Goodbye! 👋")
            break


        response = ChatBot(user_input)

        print(
            f"\n{Assistantname}: {response}\n"
        )