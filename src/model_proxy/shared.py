from typing import Callable
from yaml import safe_load
from io import StringIO
from rich import print as pp

_system_prompt = """
You are a smart assistant who helps in organizing folders. You are provided with a list of file names and you respond with how to organize these files.
Category names should not contain whitespace. Avoid adding any extra response or explaination.
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


def _gen_file_names_prompt_decorator(
    func: Callable[[any, str], str],
) -> Callable[[any, list], str]:
    def gen_file_names(self, files: list) -> str:
        resp = """
        ===

        """
        for f in files:
            resp += " - " + f + "\n"

        resp += "==="
        return func(self, resp)

    return gen_file_names


def _parse_suggestions_decorator(
    func: Callable[[any, dict], dict],
) -> Callable[[any, str], dict]:
    def parse_suggestions(self, content: str) -> dict:
        pp(f"Suggested reorganize as follows: \n {content}")
        return func(self, safe_load(StringIO(content.replace("---", ""))))

    return parse_suggestions
