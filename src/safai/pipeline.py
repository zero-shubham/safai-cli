from abc import ABC, abstractmethod
from .config import Config, PlatformEnum
import typer
import sys
from rich import print as pp
from rich.console import Console
from pydantic import ValidationError
from pathlib import Path
from configparser import ConfigParser
from .model_proxy import ProxyCreator
from .directory_handler import DirectoryHandler

try:
    import platformdirs
except ImportError:
    platformdirs = None


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

        ai = ProxyCreator.create(self.cfg)

        with Console().status("[bold green]In process...\n") as status:
            for directory, files in dir_files.items():
                status.console.print(f"Currently processing {directory} \n")
                if len(files) == 0:
                    pp(f"Skipping empty folder {directory} :zero: \n")
                    continue

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
        cfg_parser = ConfigParser()
        cfg = {}

        # Determine config file paths to check
        config_paths = []
        
        # For non-Linux systems, check platform-specific config directory first
        if sys.platform != "linux" and platformdirs is not None:
            platform_config_dir = Path(platformdirs.user_config_dir("safai"))
            config_paths.append(platform_config_dir / "config")
            config_paths.append(platform_config_dir / "config.ini")
        
        # Always check ~/.safai as fallback
        config_paths.append(Path.home() / ".safai")
        
        # Try each config path until we find one that exists
        for config_path in config_paths:
            if config_path.exists():
                cfg_parser.read(config_path)
                break

        # Load config section if it exists
        if cfg_parser.has_section("config"):
            cfg.update(cfg_parser["config"])
        
        if platform == PlatformEnum.np:
            platform = cfg.get("platform")

        # Load platform-specific section if it exists
        if platform and cfg_parser.has_section(platform):
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
