from anthropic import Client
from typing import List
from .shared import (
    _system_prompt,
    _parse_suggestions_decorator,
    _gen_file_names_prompt_decorator,
)


class ClaudeProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = Client(api_key=api_key)

    @_gen_file_names_prompt_decorator
    def _generate_file_names_prompt(self, prompt: str) -> str:
        return prompt

    @_parse_suggestions_decorator
    def _parse_suggested_dir_structure(self, parse_content: dict) -> dict:
        return parse_content

    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        if len(self.content) == 0:
            self.content.append(
                {"role": "user", "content": self._generate_file_names_prompt(files)}
            )
        else:
            self.content.append({"role": "user", "content": user_feeback})

        response = self.client.messages.create(
            model=self.model,
            system=_system_prompt,
            messages=self.content,
            max_tokens=1000,
        )

        self.content.append({"role": "assistant", "content": response.content[0].text})

        return self._parse_suggested_dir_structure(response.content[0].text)
