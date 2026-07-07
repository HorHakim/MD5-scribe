from config import STT_MODEL
from agent import Agent


class SpeechToTextAgent(Agent):
	def __init__(self):
		super().__init__()


	def get_text_from_audio(self, audio_file_path):
		
		with open(audio_file_path, "rb") as file:

			transcription = self.client.audio.transcriptions.create(
				file=file,
				model=STT_MODEL,
				response_format="json",
				temperature=0.0
			)

			return transcription.text



if __name__ == "__main__":
	
	speech_to_text_agent = SpeechToTextAgent()


	audio_file_path = "./data/AUDIO.mp3"
	transcription_text = speech_to_text_agent.get_text_from_audio(audio_file_path)

	print(transcription_text)