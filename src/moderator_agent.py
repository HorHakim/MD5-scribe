from config import LLM_MODEL
from agent import Agent

import json


class ModeratorAgent(Agent):
	def __init__(self):
		super().__init__()


	def moderate_transcript(self, transcription_text):

		chat_completion = self.client.chat.completions.create(
			messages=[
				{
					"role": "system",
					"content": Agent.read_file("./prompts/moderator_prompt_system.txt")
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

		moderation = json.loads(chat_completion.choices[0].message.content)

		return moderation


if __name__ == "__main__":
	summary_agent_object = ModeratorAgent()

	transcription_text = Agent.read_file("./data/transcription_text.txt")

	moderation = summary_agent_object.moderate_transcript(transcription_text)

	print(moderation)

	prompt_injection_text = Agent.read_file("./data/injection_transcription_text.txt")

	injection_moderation = summary_agent_object.moderate_transcript(prompt_injection_text)

	print(injection_moderation)