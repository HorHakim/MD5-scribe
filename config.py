from dotenv import load_dotenv
import os

from groq import Groq

load_dotenv()

STT_MODEL="whisper-large-v3-turbo"
LLM_MODEL="openai/gpt-oss-120b"

try :
	GROQ_API_KEY=os.environ["GROQ_API_KEY"]
except:
	raise(Exception("The groq api does not exist"))
