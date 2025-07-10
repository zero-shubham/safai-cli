from abc import ABC, abstractmethod
from typing import List, Union
from safai.config import Config, PlatformEnum
from safai.model_proxy.gemini import GeminiProxy
from safai.model_proxy.openai import OpenaiProxy
from safai.model_proxy.claude import ClaudeProxy
from yaml import safe_load
from io import StringIO
from rich import print as pp


class AIProxy(ABC):
    @abstractmethod
    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        pass


class ProxyCreator:
    @classmethod
    def create(cls, cfg: Config) -> AIProxy:
        if cfg.platform == PlatformEnum.gemini:
            return ProxyAdaper(GeminiProxy(cfg.api_key, cfg.model))
        if cfg.platform == PlatformEnum.openai:
            return ProxyAdaper(OpenaiProxy(cfg.api_key, cfg.model))
        if cfg.platform == PlatformEnum.claude:
            return ProxyAdaper(ClaudeProxy(cfg.api_key, cfg.model))
        raise Exception(
            "unsupported platform type provided. expected values: gemini, openai, claude"
        )


class ProxyAdaper:
    def __init__(self, proxy: Union[ClaudeProxy, OpenaiProxy, GeminiProxy]):
        self.proxy = proxy

    def _generate_file_names_prompt(self, files: List[str]) -> str:
        resp = """
        ===

        """
        for f in files:
            resp += " - " + f + "\n"

        resp += "==="
        return resp

    def _parse_suggested_dir_structure(self, content: str) -> dict:
        pp(f"Suggested reorganize as follows: \n {content}")

        content = content.replace("---", "", 1)

        if "---" in content:
            split_content = content.split("---")
            if len(split_content) > 0:
                content = split_content[0]
        
        return safe_load(StringIO(content))

    def get_suggestion(self, files: List[str], user_feeback: str = "") -> dict:
        return self._parse_suggested_dir_structure(
            self.proxy.get_suggestion(
                self._generate_file_names_prompt(files), user_feeback=user_feeback
            )
        )
