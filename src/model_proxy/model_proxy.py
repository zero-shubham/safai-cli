from abc import ABC, abstractmethod
from typing import List
from src.config import Config, PlatformEnum
from src.model_proxy.gemini import GeminiProxy
from src.model_proxy.openai import OpenaiProxy
from src.model_proxy.claude import ClaudeProxy


class AIProxy(ABC):
    @abstractmethod
    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        pass


class ProxyCreator:
    @classmethod
    def create(cls, cfg: Config) -> AIProxy:
        if cfg.platform == PlatformEnum.gemini:
            return GeminiProxy(cfg.api_key, cfg.model)
        if cfg.platform == PlatformEnum.openai:
            return OpenaiProxy(cfg.api_key, cfg.model)
        if cfg.platform == PlatformEnum.claude:
            return ClaudeProxy(cfg.api_key, cfg.model)
        raise Exception(
            "unsupported platform type provided. expected values: gemini, openai, claude"
        )
