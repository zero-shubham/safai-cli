from abc import ABC, abstractmethod
from typing import List
from src.config import Config, PlatformEnum
from src.model_proxy.gemini import GeminiProxy


class AIProxy(ABC):
    @abstractmethod
    def get_suggestion(self, files: List[str]) -> dict:
        pass


class ProxyCreator:
    @classmethod
    def create(cls, cfg: Config) -> AIProxy:
        if cfg.platform == PlatformEnum.gemini:
            return GeminiProxy(cfg.api_key, cfg.model)
