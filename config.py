import os
from dotenv import load_dotenv
ACTIVE_TIMEOUT = 30
MEMORY_FILE = "memory.json"
load_dotenv()
DESKTOP = os.path.join(os.environ.get("USERPROFILE"), "OneDrive", "Desktop")
START_MENU = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")

SPEAK_ENABLED = True  # default mode

CONVERSATION_HISTORY_LIMIT = 20

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# AI settings
GROQ_MODEL = "llama-3.3-70b-versatile"           # fast + smart, free tier
OLLAMA_MODEL = "mistral"
DEFAULT_AI_MODE = "groq" 