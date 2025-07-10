from openai import Client
from typing import List
from yaml import safe_load
from io import StringIO
from .shared import (
    _system_prompt,
)


class OpenaiProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = Client(api_key=api_key)

    def get_suggestion(self, files_prompt: str, user_feeback: str = "") -> str:
        if len(self.content) == 0:
            self.content.append({"role": "user", "content": files_prompt})
        else:
            self.content.append({"role": "user", "content": user_feeback})

        response = self.client.responses.create(
            model=self.model, instructions=_system_prompt, input=self.content
        )
        self.content.append({"role": "assistant", "content": response.output_text})

        return response.output_text
