# Jerry — AI Voice Assistant 🎙️

A Python-based intelligent voice assistant for Windows that combines 
speech recognition, AI understanding, and system control.

## Features
-  Wake word activation ("Hello Jerry")
-  AI-powered understanding via Groq (LLaMA 3.3)
-  Text-to-speech responses
-  Opens desktop apps and websites
-  System control (volume, brightness, shutdown)
-  Persistent memory and self-learning
-  Web dashboard with real-time chat

## Tech Stack
- Python 3.x
- Groq API (LLaMA 3.3-70b)
- Whisper (speech-to-text)
- Pyttsx3 (text-to-speech)
- porcupine (wake word)
- Flask + SocketIO (web dashboard)
- RapidFuzz (app matching)

## Setup

### 1. Clone the repo
git clone https://github.com/yourusername/jerry.git
cd jerry

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set up environment variables
Create a .env file in the root folder:
GROQ_API_KEY=your-groq-api-key
ACCESS_KEY=your-porcupine-access-key

### 4. Run Jerry
python main.py

### 5. Open dashboard
http://127.0.0.1:5000

## Project Structure
jerry/
├── core/          # Assistant brain, intent, routing
├── services/      # App, web, AI, system services
├── memory/        # Persistent memory manager
├── voice/         # Listener, speaker, wake word
├── ui/            # Flask dashboard
├── config.py      # Configuration
└── main.py        # Entry point