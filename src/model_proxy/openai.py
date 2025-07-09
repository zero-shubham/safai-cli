from openai import Client
from typing import List
from yaml import safe_load
from io import StringIO
from .shared import (
    _system_prompt,
    _gen_file_names_prompt_decorator,
    _parse_suggestions_decorator,
)


class OpenaiProxy:
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

        response = self.client.responses.create(
            model=self.model, instructions=_system_prompt, input=self.content
        )
        self.content.append({"role": "assistant", "content": response.output_text})

        return self._parse_suggested_dir_structure(response.output_text)
