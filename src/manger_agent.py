from speech_to_text_agent import SpeechToTextAgent 
from summary_agent import SummaryAgent

class ManagerAgent:
	def __init__(self):
		self.speech_to_text_agent_object = SpeechToTextAgent()
		self.summary_agent_object = SummaryAgent()


	def summaries_audio(self, audio_file_path):
		transcription_text = self.speech_to_text_agent_object.get_text_from_audio(audio_file_path)
		text_summary_dict = self.summary_agent_object.summarise_text(transcription_text)

		return text_summary_dict



if __name__ == "__main__":
	audio_file_path = "./data/AUDIO.mp3"
	manager_agent_object = ManagerAgent()
	text_summary_dict = manager_agent_object.summaries_audio(audio_file_path)

	for key, value in text_summary_dict.items():
		print(f"{key}: {value}")
		print("---")