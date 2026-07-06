from config import STT_MODEL
from agent import Agent


class SpeechToTextAgent(Agent):
	def __init__(self):
		super().__init__()


	def get_text_from_audio(self, file_path):
		
		with open(file_path, "rb") as file:

			transcription = self.client.audio.transcriptions.create(
				file=file,
				model=STT_MODEL,
				response_format="json",
				temperature=0.0
			)

			return transcription.text



if __name__ == "__main__":
	
	speech_to_text_agent = SpeechToTextAgent()


	file_path = "./data/AUDIO.mp3" # Replace with your audio file
	extracted_text = speech_to_text_agent.get_text_from_audio(file_path)

	print(extracted_text)