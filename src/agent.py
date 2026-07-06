from config import GROQ_API_KEY
from groq import Groq


class Agent:
	def __init__(self):
		self.client = Groq(api_key=GROQ_API_KEY)