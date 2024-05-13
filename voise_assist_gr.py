import speech_recognition as sr
from gtts import gTTS
import os

def listen():
    # Use the microphone as source for input.
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

def respond(text):
    """Process the text and determine a response."""
    response = process_command(text)
    tts = gTTS(text=response, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

def process_command(text):
    """Custom processing logic."""
    if "turn on the light" in text.lower():
        return "Turning on the light."
    else:
        return "Command not recognized."

# Main loop
r = sr.Recognizer()
while True:
    command = listen()
    respond(command)
