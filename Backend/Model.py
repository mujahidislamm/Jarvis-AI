import cohere
from rich import print
import os
from dotenv import dotenv_values

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))

CohereAPIKey = env_vars.get("CohereAPIKey")

if not CohereAPIKey:
    raise ValueError(
        "CohereAPIKey was not found in your .env file."
    )


# ============================================================
# INITIALIZE COHERE
# ============================================================

co = cohere.Client(api_key=CohereAPIKey)


# ============================================================
# AVAILABLE FUNCTIONS / TASKS
# ============================================================

funcs = [
    "exit",
    "general",
    "realtime",
    "open",
    "close",
    "play",
    "generate image",
    "system",
    "content",
    "google search",
    "youtube search",
    "reminder"
]


# ============================================================
# DECISION-MAKING PROMPT
# ============================================================

preamble = """
You are a very accurate Decision-Making Model for a personal AI
assistant called Jarvis.

Your ONLY job is to classify the user's query.

DO NOT answer the user's question.
DO NOT explain your decision.
ONLY return the correct task classification.

AVAILABLE CLASSIFICATIONS:

1. general
Use this when the query can be answered by an AI model and does
not specifically require current information.

Examples:
"who was Akbar?"
-> general who was Akbar?

"how can I study more effectively?"
-> general how can I study more effectively?

"can you help me with this math problem?"
-> general can you help me with this math problem?

"Thanks, I really liked it."
-> general Thanks, I really liked it.

"who is he?"
-> general who is he?

"what is his net worth?"
-> general what is his net worth?

"tell me more about him."
-> general tell me more about him.

Questions about the current time, date, day, month, or year
should also be classified as general.

Example:
"what is the time?"
-> general what is the time?


2. realtime
Use this when the query requires current or up-to-date information.

Examples:
"who is the Indian Prime Minister?"
-> realtime who is the Indian Prime Minister?

"tell me about Facebook's recent update."
-> realtime tell me about Facebook's recent update.

"what is today's news?"
-> realtime what is today's news?

"what is today's headline?"
-> realtime what is today's headline?

"who is Akshay Kumar?"
-> realtime who is Akshay Kumar?


3. open
Use this when the user wants to open an application or website.

Example:
"open chrome"
-> open chrome

For multiple applications:
"open chrome and open firefox"
-> open chrome, open firefox


4. close
Use this when the user wants to close an application or website.

Example:
"close chrome"
-> close chrome

For multiple applications:
"close chrome and close firefox"
-> close chrome, close firefox


5. play
Use this when the user wants to play a song.

Example:
"play Let Her Go"
-> play Let Her Go

For multiple songs:
"play Believer and play Faded"
-> play Believer, play Faded


6. generate image
Use this when the user requests an image to be generated.

Example:
"generate an image of a lion"
-> generate image a lion

For multiple images:
"generate an image of a lion and a tiger"
-> generate image a lion, generate image a tiger


7. reminder
Use this when the user wants to create a reminder.

Example:
"remind me at 9 PM tomorrow to call John"
-> reminder 9 PM tomorrow call John

Include the date/time and reminder message.


8. system
Use this for computer system controls such as:

- mute
- unmute
- volume up
- volume down
- brightness
- shutdown
- restart
- sleep

Examples:
"mute the computer"
-> system mute

"turn the volume up"
-> system volume up


9. content
Use this when the user wants you to write or generate content.

Examples:
"write an email to my teacher"
-> content email to my teacher

"write a Python program"
-> content Python program

"write an application for leave"
-> content application for leave


10. google search
Use this when the user explicitly asks to search Google.

Example:
"search Google for Python tutorials"
-> google search Python tutorials


11. youtube search
Use this when the user explicitly asks to search YouTube.

Example:
"search YouTube for Python tutorials"
-> youtube search Python tutorials


12. exit
Use this when the user wants to end the conversation.

Examples:
"bye"
-> exit

"goodbye Jarvis"
-> exit

"quit"
-> exit


MULTIPLE TASKS:

If the user asks for multiple tasks, return each task separated
by a comma.

Example:
"open chrome and tell me about Mahatma Gandhi"
-> open chrome, realtime tell me about Mahatma Gandhi

Example:
"open chrome, open firefox and close notepad"
-> open chrome, open firefox, close notepad


IMPORTANT RULES:

- Return ONLY classifications.
- Do NOT answer the user's question.
- Do NOT use markdown.
- Do NOT add explanations.
- Do NOT write "(query)" literally.
- Keep the original query after the classification.
- If you cannot determine the task, use general.
"""


# ============================================================
# CHAT HISTORY / EXAMPLES
# ============================================================

ChatHistory = [
    {
        "role": "USER",
        "message": "how are you?"
    },
    {
        "role": "CHATBOT",
        "message": "general how are you?"
    },

    {
        "role": "USER",
        "message": "do you like pizza?"
    },
    {
        "role": "CHATBOT",
        "message": "general do you like pizza?"
    },

    {
        "role": "USER",
        "message": "open chrome and tell me about mahatma gandhi."
    },
    {
        "role": "CHATBOT",
        "message": "open chrome, realtime tell me about mahatma gandhi."
    },

    {
        "role": "USER",
        "message": "open chrome and open firefox"
    },
    {
        "role": "CHATBOT",
        "message": "open chrome, open firefox"
    },

    {
        "role": "USER",
        "message": "what is today's date and remind me that I have a dancing performance on 5th aug at 11pm"
    },
    {
        "role": "CHATBOT",
        "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"
    },

    {
        "role": "USER",
        "message": "chat with me."
    },
    {
        "role": "CHATBOT",
        "message": "general chat with me."
    },

    {
        "role": "USER",
        "message": "search Google for Python tutorials"
    },
    {
        "role": "CHATBOT",
        "message": "google search Python tutorials"
    },

    {
        "role": "USER",
        "message": "search YouTube for relaxing music"
    },
    {
        "role": "CHATBOT",
        "message": "youtube search relaxing music"
    },

    {
        "role": "USER",
        "message": "mute my computer"
    },
    {
        "role": "CHATBOT",
        "message": "system mute"
    },

    {
        "role": "USER",
        "message": "write an email to my teacher"
    },
    {
        "role": "CHATBOT",
        "message": "content email to my teacher"
    },

    {
        "role": "USER",
        "message": "bye Jarvis"
    },
    {
        "role": "CHATBOT",
        "message": "exit"
    }
]


# ============================================================
# FIRST LAYER DECISION MAKING MODEL
# ============================================================

def FirstLayerDMM(prompt: str = "test"):

    if not prompt or not prompt.strip():
        return ["general"]

    prompt = prompt.strip()

    try:

        stream = co.chat_stream(
            model="command-a-03-2025",
            message=prompt,
            temperature=0.0,
            chat_history=ChatHistory,
            prompt_truncation="OFF",
            connectors=[],
            preamble=preamble
        )

        response = ""

        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        # Remove newlines
        response = response.replace("\n", " ").strip()

        # Remove unnecessary spaces
        response = " ".join(response.split())

        # Split multiple tasks
        response = response.split(",")

        # Clean every task
        response = [
            task.strip()
            for task in response
            if task.strip()
        ]

        # Validate tasks
        valid_tasks = []

        for task in response:

            task_lower = task.lower()

            for func in funcs:

                if task_lower.startswith(func.lower()):

                    valid_tasks.append(task)
                    break

        # If the model returned nothing valid,
        # classify as general.
        if not valid_tasks:
            return [f"general {prompt}"]

        return valid_tasks

    except Exception as e:

        print(f"[red]Decision Model Error:[/red] {e}")

        return [f"general {prompt}"]


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("[bold cyan]Jarvis Decision Making Model Started[/bold cyan]")
    print("[yellow]Type 'exit' or 'bye' to stop.[/yellow]\n")

    while True:

        try:

            prompt = input(">>> ").strip()

            if not prompt:
                continue

            result = FirstLayerDMM(prompt)

            print(result)

            # Stop program if the model detects exit
            if any(
                task.lower().strip() == "exit"
                for task in result
            ):
                print("[bold green]Goodbye![/bold green]")
                break

        except KeyboardInterrupt:

            print("\n[bold green]Goodbye![/bold green]")
            break

        except Exception as e:

            print(f"[red]Error:[/red] {e}")
