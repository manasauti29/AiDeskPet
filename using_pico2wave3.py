import os
import subprocess
import threading
import vosk
import pyaudio
import json
import requests
import time
import sys
import tty
import termios

# Path to Pico2Wave (ensure it's installed)
PICO2WAVE_PATH = "/usr/bin/pico2wave"

# Beep before listening (requires sox)
def beep():
    os.system("play -nq -t alsa synth 0.3 sine 880")

# Function to check for ENTER key press asynchronously
def wait_for_enter():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Speak function with interruption
def speak(text):
    stop_flag = threading.Event()
    interrupt_thread = threading.Thread(target=wait_for_enter, daemon=True)
    interrupt_thread.start()
    
    if os.path.exists(PICO2WAVE_PATH):
        speech_file = "/tmp/speech.wav"
        subprocess.run([PICO2WAVE_PATH, "-w", speech_file, text])
        process = subprocess.Popen(["aplay", speech_file])
        
        while process.poll() is None:
            if not interrupt_thread.is_alive():  # ENTER pressed
                process.terminate()
                print("\nSpeech interrupted! Returning to listening mode...")
                return
        
        process.wait()
    else:
        print("Error: Pico2Wave is not installed.")

# Listen function using Vosk
def listen():
    model_path = "/home/deskpet69/Desktop/deskpet/vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print("Error: Vosk model not found at", model_path)
        return ""
    
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    
    try:
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                          input=True, frames_per_buffer=8192)
        stream.start_stream()
        
        print("Listening...")
        beep()
        
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get("text", "")
                print(f"You said: {text}")
                break
        
        stream.stop_stream()
        stream.close()
        mic.terminate()
        return text.lower()
    
    except KeyboardInterrupt:
        print("\nStopping...")
        return ""
    except Exception as e:
        print(f"Error during Vosk recognition: {e}")
        return ""

# Function to handle predefined responses
def ask_tinyllama(prompt):
    responses = {
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! How can I help?",
        "who are you": "I am an AI assistant made at 3DEXPERIENCE Lab, Dassault Systèmes.",
    }
    
    if prompt in responses:
        return responses[prompt]
    
    url = "http://localhost:11434/api/generate"
    payload = {"model": "tinyllama:latest", "prompt": prompt, "stream": False}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("response", "Error processing request")
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"
    except json.JSONDecodeError:
        return f"Error: Received unexpected response: {response.text}"

# Main loop
while True:
    user_input = listen()
    if user_input in ["exit", "quit", "stop"]:
        speak("Goodbye!")
        break
    
    if user_input:
        print(f"Processing: {user_input}")
        response = ask_tinyllama(user_input)
        print(f"AI: {response}")
        speak(response)
        time.sleep(1)  # Prevent immediate re-triggering
