from abc import ABC, abstractmethod
from .config import Config, PlatformEnum
import typer
from rich import print as pp
from rich.console import Console
from pydantic import ValidationError
from pathlib import Path
from configparser import ConfigParser
from .model_proxy import ProxyCreator
from .directory_handler import DirectoryHandler


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

        with Console().status("[bold green]In process...\n") as status:
            for directory, files in dir_files.items():
                status.console.print(f"Currently processing {directory} \n")
                if len(files) == 0:
                    pp(f"Skipping empty folder {directory} :zero: \n")
                    continue
                ai = ProxyCreator.create(self.cfg)
                suggestion = ai.get_suggestion(files)

                feedback = "n"
                while not self.cfg.one_shot:
                    status.stop()
                    feedback = Console(record=True).input(
                        "\nPlease provide any feedback if required (n to accept / s to skip - current plan): "
                    )

                    if feedback == "n" or feedback == "s":
                        break

                    status.start()
                    suggestion = ai.get_suggestion(files, feedback)

                if feedback != "s":
                    dh.restructure_directory(directory, suggestion)

        pp("\nHappy decluttering! :sparkles:")


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
            config_from_file = cls._load_config_file_(
                config.get("platform", PlatformEnum.np)
            )
            for k, v in config.items():
                if not v and k not in ["one_shot", "recursive"]:
                    if config_from_file.get(k, ""):
                        config[k] = config_from_file[k]

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
            pp(f"Unexpected error: {str(e)}")
            raise typer.Exit()
