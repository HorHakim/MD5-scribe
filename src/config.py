from dotenv import load_dotenv
from pathlib import Path
import os

from groq import Groq

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

STT_MODEL="whisper-large-v3-turbo"
LLM_MODEL="openai/gpt-oss-120b"

try :
	GROQ_API_KEY=os.environ["GROQ_API_KEY"]
except:
	raise(Exception("The groq api does not exist"))
