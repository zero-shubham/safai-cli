from anthropic import Client
from typing import List
from .shared import (
    _system_prompt,
)


class ClaudeProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = Client(api_key=api_key)

    def get_suggestion(self, files_prompt: str, user_feeback: str = "") -> str:
        if len(self.content) == 0:
            self.content.append({"role": "user", "content": files_prompt})
        else:
            self.content.append({"role": "user", "content": user_feeback})

        response = self.client.messages.create(
            model=self.model,
            system=_system_prompt,
            messages=self.content,
            max_tokens=1000,
        )

        self.content.append({"role": "assistant", "content": response.content[0].text})

        return response.content[0].text
