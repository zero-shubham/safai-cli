from pydantic import BaseModel, field_validator, constr, ValidationInfo
from enum import Enum
from rich import print as pp


class PlatformEnum(str, Enum):
    claude = "claude"
    openai = "openai"
    gemini = "gemini"
    np = "not provided"


_default_models = {PlatformEnum.gemini: "gemini-1.5-flash"}


class Config(BaseModel):
    path: constr(strip_whitespace=True, min_length=1)
    platform: PlatformEnum
    api_key: constr(strip_whitespace=True, min_length=8)
    one_shot: bool
    recursive: bool
    model: str

    @field_validator("platform")
    def valid_plaform(cls, v: PlatformEnum):
        if v == PlatformEnum.np:
            raise ValueError("platform not provided")
        return v

    @field_validator("model")
    def valid_model(cls, v: str, values: ValidationInfo, **kwargs):
        if v == "":
            default = _default_models[values.data["platform"]]
            pp(f"Model value not provided defaulting to {default}")
            return default
        return v
