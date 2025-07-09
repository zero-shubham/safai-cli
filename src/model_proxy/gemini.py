from google import genai
from google.genai import types
from typing import List
from yaml import safe_load, safe_dump
from io import StringIO

_system_prompt = """
You are a smart assistant who helps in organizing folders. You are provided with a list of file names and you respond with how to organize these files.
Category names should not contain whitespace.
For example:
Input: 
===
    - MeetingMinutes.docx
    - ResearchPaper.pdf
    - VacationPhoto.jpg
    - CompanyLogo.png
    - LectureRecording.mp3
    - ProductDemo.mp4
    - SoftwareUpdate.exe
    - SystemBackup.iso
    - ProjectPlan.xlsx
    - PresentationDraft.pptx
===
Output: 
---
Documents:
  - MeetingMinutes.docx
  - ResearchPaper.pdf
  - ProjectPlan.xlsx
  - PresentationDraft.pptx
Media:
  Images:
    - VacationPhoto.jpg
    - CompanyLogo.png
  Audio:
    - LectureRecording.mp3
  Video:
    - ProductDemo.mp4
SystemFiles:
  - SoftwareUpdate.exe
  - SystemBackup.iso
---
"""


class GeminiProxy:
    def __init__(self, api_key: str, model: str):
        self.model = model
        self.content = []
        self.client = genai.Client(api_key=api_key)

    def __generate_file_names_prompt(self, files: List[str]) -> str:
        resp = """
        ===
        
        """
        for f in files:
            resp += " - " + f + "\n"

        resp += "==="
        return resp

    def __parse_suggested_dir_structure(self, content: str) -> dict:
        return safe_load(StringIO(content.replace("---", "")))

    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        if len(self.content) == 0:
            self.content.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text=self.__generate_file_names_prompt(files)
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

        return self.__parse_suggested_dir_structure(response.text)
