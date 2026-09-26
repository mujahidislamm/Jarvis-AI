import json
import datetime
from dotenv import dotenv_values
from groq import Groq

# Load environment variables
env_vars = dotenv_values(".env")

Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("GroqAPIKey is missing from your .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message
System = f"""
Hello, you are a very accurate and advanced AI chatbot named {Assistantname}.

Rules:
- Do not tell the time unless I ask.
- Do not talk too much.
- Reply only in English.
- Answer the question directly.
- Do not provide unnecessary notes.
- Never mention your training data.
"""

SystemChatBot = [
    {
        "role": "system",
        "content": System
    }
]


# Load previous messages
def load_messages():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        return []


# Save messages
def save_messages(messages):
    with open("Data/ChatLog.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4)


# Get current date and time
def RealtimeInformation():

    current_date_time = datetime.datetime.now()

    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = "Please use this real-time information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour}:{minute}:{second}\n"

    return data


# Clean response
def AnswerModifier(answer):

    lines = answer.split("\n")

    non_empty_lines = [
        line for line in lines
        if line.strip()
    ]

    return "\n".join(non_empty_lines)


# Chatbot
def ChatBot(Query):

    messages = load_messages()

    messages.append({
        "role": "user",
        "content": Query
    })

    try:

        completion = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=(
                SystemChatBot
                + [
                    {
                        "role": "system",
                        "content": RealtimeInformation()
                    }
                ]
                + messages
            ),

            max_completion_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        Answer = ""

        # Read streaming response
        for chunk in completion:

            if not chunk.choices:
                continue

            content = chunk.choices[0].delta.content

            if content:
                print(content, end="", flush=True)
                Answer += content

        print()

        if not Answer:
            print("No answer generated.")
            return ""

        Answer = Answer.replace("</s>", "")

        messages.append({
            "role": "assistant",
            "content": Answer
        })

        save_messages(messages)

        return AnswerModifier(Answer)

    except Exception as e:

        print(f"\nError: {e}")

        return "Sorry, I could not process your request."


# Main program
if __name__ == "__main__":

    while True:

        user_input = input("ENTER YOUR QUESTION: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        ChatBot(user_input)