from pydantic import BaseModel, field_validator, constr, ValidationInfo
from enum import Enum
from rich import print as pp
from pathlib import Path
from typing import List


class PlatformEnum(str, Enum):
    claude = "claude"
    openai = "openai"
    gemini = "gemini"
    np = "not provided"


_default_models = {
    PlatformEnum.gemini: "gemini-1.5-flash",
    PlatformEnum.openai: "o4-mini",
    PlatformEnum.claude: "claude-3-7-sonnet-latest",
}


class Config(BaseModel):
    path: Path
    platform: PlatformEnum
    api_key: constr(strip_whitespace=True, min_length=8)
    one_shot: bool
    recursive: bool
    model: str
    ignore: List[str]

    @field_validator("platform")
    def valid_plaform(cls, v: PlatformEnum):
        if v == PlatformEnum.np:
            raise ValueError("platform not provided")
        return v

    @field_validator("model")
    def valid_model(cls, v: str, values: ValidationInfo, **kwargs):
        if v == "":
            default = _default_models[values.data["platform"]]
            pp(
                f"Model value not provided defaulting to [bold blue]{default}[/bold blue]\n"
            )
            return default
        return v
