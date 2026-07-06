import os
import json
from groq import Groq


from config import GROQ_API_KEY, STT_MODEL

client = Groq(api_key=GROQ_API_KEY)



def get_text_from_audio(file_path):
	with open(file_path, "rb") as file:

		transcription = client.audio.transcriptions.create(
			file=file,
			model=STT_MODEL,
			response_format="json",
			temperature=0.0
		)

		return transcription.text

if __name__ == "__main__":
	file_path = "./data/AUDIO.mp3" # Replace with your audio file!
	extracted_text = get_text_from_audio(file_path)
	print(extracted_text)