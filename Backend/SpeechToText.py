from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
from pathlib import Path
import os
import mtranslate as mt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
FILES_DIR = os.path.join(PROJECT_ROOT, "Frontend", "Files")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# Load environment variables
env_vars = dotenv_values(os.path.join(PROJECT_ROOT, ".env"))
InputLanguage = env_vars.get("InputLanguage")

# HTML for Speech Recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language in HTML code
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the HTML to a file
voice_html_path = os.path.join(DATA_DIR, "Voice.html")
with open(voice_html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get the file URI for the generated HTML page
Link = Path(voice_html_path).as_uri()

# Set up Chrome WebDriver with specific options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize WebDriver
Service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=Service, options=chrome_options)

# Path to temp directory
TempDirPath = FILES_DIR

# Helper function to set assistant status
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify query by adding punctuation
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Universal translation function
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition
def SpeechRecognition():
    driver.get(Link)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower() == "en":
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))

        except Exception as e:
            pass

# Main function to loop speech recognition
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)