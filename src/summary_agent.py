from config import LLM_MODEL
from agent import Agent

import json

class SummaryAgent(Agent):
	def __init__(self):
		super().__init__()


	def summarise_text(self, transcription_text):

		chat_completion = self.client.chat.completions.create(
			messages=[
				{
					"role": "system",
					"content": Agent.read_file("./prompts/summary_prompt_system.txt")
				},
				{
					"role": "user",
					"content": transcription_text,
				}
			],
			model=LLM_MODEL,
			response_format={"type": "json_object"},
			temperature=0,
		)

		text_summary_dict = json.loads(chat_completion.choices[0].message.content)

		return text_summary_dict


if __name__ == "__main__":
	summary_agent_object = SummaryAgent()

	transcription_text = Agent.read_file("./data/transcription_text.txt")

	text_summary_dict = summary_agent_object.summarise_text(transcription_text)
	
	print(text_summary_dict)