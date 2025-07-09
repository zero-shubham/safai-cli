from abc import ABC, abstractmethod
from src.config import Config, PlatformEnum
import typer
from rich import print as pp
from pydantic import ValidationError
from pathlib import Path
from configparser import ConfigParser
from model_proxy import ProxyCreator
from directory_handler import DirectoryHandler


class Orchestrator(ABC):
    @abstractmethod
    def run(self):
        pass


class Pipeline:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def run(self):
        dh = DirectoryHandler(self.cfg.path, self.cfg.ignore)
        dir_files = dh.list_directory_files(recursive=self.cfg.recursive)

        for directory, files in dir_files.items():
            ai = ProxyCreator.create(self.cfg)
            if len(files) == 0:
                pp(f"Skipping empty folder {directory}")
                continue
            suggestion = ai.get_suggestion(files)
            dh.restructure_directory(directory, suggestion)

        pp("complete.")


class PipelineCreator:
    @classmethod
    def _load_config_file_(cls, platform: PlatformEnum) -> dict:
        home = Path.home()
        cfg_parser = ConfigParser()
        cfg_parser.read(f"{home}/.safai")
        cfg = {}

        cfg.update(cfg_parser["config"])
        if platform == PlatformEnum.np:
            platform = cfg.get("platform")

        if cfg_parser.has_section(platform):
            cfg.update(cfg_parser[platform])

        return cfg

    @classmethod
    def create(cls, config: dict) -> Orchestrator:
        try:
            config.update(
                cls._load_config_file_(config.get("platform", PlatformEnum.np))
            )
            cfg = Config(**config)

            return Pipeline(cfg)
        except ValidationError as e:
            err_msg = "\nAll required configs are not provided, make sure to pass --model and --api_key or add these in $HOMEDIR/.safai\n"
            for err in e.errors():
                loc = err.get("loc", ())
                loc_str = ", ".join(loc)
                err_msg += "\n" + err.get("msg", "") + " - " + loc_str

            pp(err_msg)
            raise typer.Exit()
        except Exception as e:
            pp(f"Unexpected error: {e}")
            raise typer.Exit()
