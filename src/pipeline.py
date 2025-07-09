from abc import ABC, abstractmethod
from src.config import Config
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
        pp(self.cfg)

        dh = DirectoryHandler(self.cfg.path)
        dir_files = dh.list_directory_files(recursive=True)

        ai = ProxyCreator.create(self.cfg)

        for directory, files in dir_files.items():
            pp(directory, files)

            # suggestion = ai.get_suggestion(files)

            # pp(suggestion)


class PipelineCreator:
    @classmethod
    def __load_config_file__(cls) -> dict:
        home = Path.home()
        cfg_parser = ConfigParser()
        cfg_parser.read(f"{home}/.safai")
        cfg = {}

        for section in cfg_parser.sections():
            cfg.update(cfg_parser[section])

        return cfg

    @classmethod
    def create(cls, config: dict) -> Orchestrator:
        try:
            config.update(cls.__load_config_file__())
            pp(config)
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
