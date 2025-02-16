from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")  # Default to English if not set

# HTML Speech Recognition Code
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
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;  // Update text content instead of appending
            };

            recognition.start();
        }

        function stopRecognition() {
            if (recognition) recognition.stop();
        }
    </script>
</body>
</html>'''

# Set the input language
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save the HTML file
html_path = os.path.join(os.getcwd(), "Data", "Voice.html")
os.makedirs(os.path.dirname(html_path), exist_ok=True)
with open(html_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Chrome WebDriver Setup
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")

# REMOVE headless mode (speech recognition doesn’t work in headless mode)
# chrome_options.add_argument("--headless=new")  

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Path for status files
temp_dir = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(temp_dir, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(temp_dir, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's"]

    if any(word + " " in new_query for word in question_words):
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "?"
    else:
        if new_query[-1] not in ['.', '?', '!']:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

def SpeechRecognition():
    driver.get("file:///" + html_path)

    # Start speech recognition
    driver.find_element(By.ID, "start").click()
    print("[INFO] Listening for speech...")

    start_time = time.time()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text.strip()

            if Text:
                driver.find_element(By.ID, "end").click()
                print("[INFO] Speech Detected:", Text)

                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating ...")
                    return QueryModifier(UniversalTranslator(Text))
            
            # Exit loop after 10 seconds if no speech is detected
            if time.time() - start_time > 10:
                print("[INFO] No speech detected. Restarting...")
                return None
        except Exception as e:
            print("Error:", e)
            break

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text:
            print(Text)
