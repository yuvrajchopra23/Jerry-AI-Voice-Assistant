# Jerry — AI Voice Assistant 🎙️

Jerry is an intelligent voice assistant for Windows built entirely from scratch in Python. 
Unlike traditional voice assistants that rely on rigid command patterns, Jerry uses 
**Groq's LLaMA 3.3** large language model to understand natural language — meaning you 
can talk to him the way you'd talk to a person.

## What makes Jerry different?

Most voice assistants match your command against a fixed list of rules.
Jerry understands **intent** — you don't need to say the exact right words.
Say "pull up youtube", "launch youtube" or "open youtube" — he knows what you mean.

## What can Jerry do?

-  **Wake word activation** — say "Hello Jerry" to wake him up
-  **Natural language understanding** — powered by LLaMA 3.3 via Groq API
-  **Voice responses** — speaks back using text-to-speech (toggleable)
-  **App control** — opens any installed desktop or Microsoft Store app
-  **Website control** — opens any website in your browser
-  **System control** — adjust volume, brightness, shutdown, restart, sleep
-  **Persistent memory** — remembers facts and learned commands across sessions
-  **Self-learning** — learns new commands permanently from conversation
-  **Web dashboard** — real-time chat UI with system controls at localhost:5000
-  **Dual input** — works via both voice and text simultaneously

## How it works

1. Jerry listens for the wake word using Porcupine
2. Captures your voice and transcribes it using Groq Whisper
3. Sends the text to LLaMA 3.3 with your conversation history
4. LLaMA decides the action (open app, answer question, system control, etc.)
5. Jerry executes the action and responds — both on screen and by voice
6. Everything is saved to memory for future conversations

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
