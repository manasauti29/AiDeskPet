# AiDeskPet
AiDeskPet: Offline AI Chatbot for Ubuntu OS on Raspberry Pi 5
AiDeskPet is an offline AI-powered chatbot built using Ollama LLM that runs seamlessly on Ubuntu OS and is optimized for the Raspberry Pi 5 (8GB RAM variant). Designed for users who require a local, privacy-focused solution, AiDeskPet provides a responsive and intelligent conversational agent without needing an internet connection.

Key Features:

Offline Functionality: Operates entirely offline, ensuring privacy and data security for all interactions.

Optimized for Raspberry Pi 5 (8GB RAM): Tailored for the Raspberry Pi 5, leveraging its 8GB RAM variant for efficient performance and low latency.

Ollama LLM Integration: Powered by Ollama's Local Language Models (LLMs), AiDeskPet offers high-quality natural language understanding and conversation capabilities.

Lightweight and Efficient: Designed to be resource-efficient, AiDeskPet ensures smooth operation even on the limited hardware of a Raspberry Pi.

This project is ideal for users looking for an AI assistant that works independently of cloud services, with a focus on privacy and reliability. Whether for personal use, research, or local deployment in IoT applications, AiDeskPet provides a robust and flexible AI solution for offline environments.

Installation:
Clone the repository:
git clone https://github.com/manasauti29/AiDeskPet.git 

To set up the environment on Ubuntu OS running on Raspberry Pi 5.
Download VS code, python3.10+, ollama

To download ollama
Install with one command:
curl -fsSL https://ollama.com/install.sh | sh <br>
Then download a LLM model in Ollama 
ollama run tinyllama

Run the Requirements.txt to install all the dependencies
To set up the environment on Ubuntu OS running on Raspberry Pi 5.

Dependencies 
1)	Python 3.9
2)	Ensure Ollama is installed using curl -fsSL https://ollama.com/install.sh | sh
3)	Ensure pip is installed using sudo apt install python3-pip
4)	Ensure Vs code is installed using sudo apt install ./code_1.89.0-linux-x64.deb
5)	pip install vosk
6)	pip install pyaudio (on linux before pyaudio u have to run sudo apt-get install portaudio19-dev)
7)	install pico2wave using sudo apt-get install libttspico-utils
8)	then install sox using sudo apt-get install libasound2-plugins lubasound2-python libsox-fmt-all
9)	then sudo apt-get install sox

How to run the program:
1)	Go to terminal
2)	cd to the folder (cd Desktop, cd deskpet) 
If not then create a virtual env using python -m <env name> venv and install the requirements using pip install -r requirements if available or install all the dependencies one by one from the terminal.
3)	Run the virtual env named “venv” (source venv/bin/activate)
4)	Make sure that Ollama is running for that do ollama serve in terminal
5)	Then sure that the LLM used in the code (here gemma3/tinyllama:latest) is actually downloaded, so do that using ollama pull <model_name> for eg ollama pull gemma3.1b
6)	Open code from there in that venv (code .)
7)	Connect a headphone with mic to the R pi, and check if audio is working by playing yt, if audio is not audible then u have to update the ALSA files.
8)	Run the code in the VS code through the top right button in the vs code screen.


Enjoy an offline, local AI chatbot powered by Ollama LLM!

Technologies Used:
Ollama LLM for natural language processing
Raspberry Pi 5 (8GB RAM variant)
Ubuntu OS

