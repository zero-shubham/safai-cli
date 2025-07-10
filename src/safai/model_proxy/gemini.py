from google import genai
from google.genai import types
from .shared import (
    _system_prompt,
)


class GeminiProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = genai.Client(api_key=api_key)

    def get_suggestion(self, files_prompt: str, user_feeback: str = "") -> str:
        if len(self.content) == 0:
            self.content.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=files_prompt)],
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

        return response.text
