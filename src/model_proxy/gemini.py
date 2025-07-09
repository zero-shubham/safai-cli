from google import genai
from google.genai import types
from typing import List
from .shared import (
    _system_prompt,
    _gen_file_names_prompt_decorator,
    _parse_suggestions_decorator,
)


class GeminiProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = genai.Client(api_key=api_key)

    @_gen_file_names_prompt_decorator
    def _generate_file_names_prompt(self, prompt: str) -> str:
        return prompt

    @_parse_suggestions_decorator
    def _parse_suggested_dir_structure(self, parse_content: dict) -> dict:
        return parse_content

    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        if len(self.content) == 0:
            self.content.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=self._generate_file_names_prompt(files)
                        )
                    ],
                )
            )
        else:
            self.content.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_feeback)],
                )
            )

        response = self.client.models.generate_content(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=_system_prompt,
                temperature=0.3,
            ),
            contents=self.content,
        )
        self.content.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=response.text)],
            )
        )

        return self._parse_suggested_dir_structure(response.text)
