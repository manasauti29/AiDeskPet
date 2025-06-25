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
import tkinter as tk

# Path to Pico2Wave (ensure it's installed)
PICO2WAVE_PATH = "/usr/bin/pico2wave"

# Global control for GUI animation
is_speaking = False
bars = []
canvas = None

# Beep before listening (requires sox)
def beep():
    os.system("play -nq -t alsa synth 0.3 sine 880")

# ENTER key interrupt
def wait_for_enter():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# SPEAK with animation
def speak(text):
    global is_speaking
    interrupt_thread = threading.Thread(target=wait_for_enter, daemon=True)
    interrupt_thread.start()

    if os.path.exists(PICO2WAVE_PATH):
        speech_file = "/tmp/speech.wav"
        subprocess.run([PICO2WAVE_PATH, "-w", speech_file, text])
        process = subprocess.Popen(["aplay", speech_file])

        is_speaking = True  # Start mouth animation

        while process.poll() is None:
            if not interrupt_thread.is_alive():
                process.terminate()
                is_speaking = False
                print("\nSpeech interrupted! Returning to listening mode...")
                return

        process.wait()
        is_speaking = False  # Stop animation
    else:
        print("Error: Pico2Wave is not installed.")

# LISTEN using Vosk
def listen():
    model_path = "/home/monday/Downloads/vosk-model-small-en-us-0.15"
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

# Get response (predefined + TinyLLaMA)
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


from PIL import Image, ImageTk

def start_gui():
    global bars, canvas, bar_colors_idle, bar_colors_speaking

    root = tk.Tk()
    root.title("AI Assistant Face")
    root.configure(bg="black")
    root.resizable(False, False)

    canvas = tk.Canvas(root, width=400, height=400, bg="black", highlightthickness=0)
    canvas.pack()

    # Load and place background image
    bg_image = Image.open("ai_face.jpg").resize((400, 400))
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)

    # Define bar properties (now at bottom)
    mouth_y_bottom = 385  # almost at bottom
    bar_x = 80            # centered visually
    bar_spacing = 10
    bar_width = 4
    bar_count = 16
    bars = []

    # Colors
    bar_colors_idle = "#6a5acd"    # purple-blue (semi-transparent feel)
    bar_colors_speaking = "#ffffff"  # white

    # Draw bars initially in idle color
    for _ in range(bar_count):
        bar = canvas.create_rectangle(bar_x, mouth_y_bottom, bar_x + bar_width,
                                      mouth_y_bottom - 20,
                                      fill=bar_colors_idle, outline="", width=0)
        bars.append(bar)
        bar_x += bar_width + bar_spacing

    # Animation loop
    def animate_mouth():
        import random
        while True:
            if is_speaking:
                for bar in bars:
                    height = random.randint(15, 35)
                    x0, _, x1, _ = canvas.coords(bar)
                    canvas.coords(bar, x0, mouth_y_bottom, x1, mouth_y_bottom - height)
                    canvas.itemconfig(bar, fill=bar_colors_speaking)
            else:
                for bar in bars:
                    x0, _, x1, _ = canvas.coords(bar)
                    canvas.coords(bar, x0, mouth_y_bottom, x1, mouth_y_bottom - 15)
                    canvas.itemconfig(bar, fill=bar_colors_idle)
            canvas.update()
            time.sleep(0.08)

    threading.Thread(target=animate_mouth, daemon=True).start()
    root.mainloop()



# Start GUI in background
gui_thread = threading.Thread(target=start_gui, daemon=True)
gui_thread.start()

# === Main Chat Loop ===
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
        time.sleep(1)
