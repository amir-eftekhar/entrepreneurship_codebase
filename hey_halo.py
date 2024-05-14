from wake_word import wake_word_listener
import threading
import speech_recognition as sr
from detect_object import main as detect_object_main
from dept_sound_wot import main as dept_soud_wot_main
from gtts import gTTS
from playsound import playsound
import tempfile

mapping = threading.Event()
mapping.set()

def provide_feedback(message):
    tts = gTTS(text=message, lang='en')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name + '.mp3')
        playsound(fp.name + '.mp3')

def listen_for_next_word():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        print("Listening for the next word...")
        audio = recognizer.listen(source, timeout=5)
    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def process_command_start(command):
    print("Processing command for 'start':", command)
    thread_hey_halo = threading.Thread(target=wake_word_listener, args=("hey halo", process_command_hey_halo))
    thread_start_map = threading.Thread(target=wake_word_listener, args=("start map", process_command_start_map))
    thread_find = threading.Thread(target=wake_word_listener, args=("find", process_command_find))
    thread_hey_halo.start()
    thread_start_map.start()
    thread_find.start()

def process_command_hey_halo(command):
    print("Processing command for 'hey halo':", command)
    thread_stop_map = threading.Thread(target=wake_word_listener, args=("stop map", process_command_stop_map))
    thread_stop_map.start()

def process_command_start_map(command):
    print("Processing command for 'start map':", command)
    dept_soud_wot_main(mapping)

def process_command_stop_map(command):
    print("Processing command for 'stop map':", command)
    mapping.clear()

def process_command_find(command):
    print("Processing command for 'find':", command)
    provide_feedback("Please say the name of the object to find.")
    target_object = listen_for_next_word()
    if target_object:
        provide_feedback(f"Searching for {target_object}.")
        detect_object_main(target_object)
    else:
        provide_feedback("Could not recognize the object name. Please try again.")

wake_word_listener("start", process_command_start)
