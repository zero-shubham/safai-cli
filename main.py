import typer
from typing_extensions import Annotated
from src.config import PlatformEnum
from src.pipeline import PipelineCreator

app = typer.Typer(
    name="Safai", help="CLI that cleans yup folder by intelligently organizing it."
)


@app.command()
def main(
    path: str,
    platform: Annotated[
        PlatformEnum, typer.Option("--platform", "-pl", help="AI platform to use")
    ] = PlatformEnum.np,
    one_shot: Annotated[bool, typer.Option("--one_shot", "-o")] = False,
    api_key: Annotated[
        str, typer.Option("--api_key", "-a", help="API Key for AI Model")
    ] = "",
    model: Annotated[
        str, typer.Option("--model", "-m", help="Model to use as per platform")
    ] = "",
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Recursively organize sub-directories"),
    ] = False,
):
    """
    CLI that cleans yup folder by intelligently organizing it.\n

    By default except `path` all other options will be loaded from $HOMEDIR/.safai when not provided

    path : is required, this is path to the directory that needs to be organized

    --platform: AI platform to use

    --one_shot: Organize without any feedback from user

    --api_key: API Key for the AI Model

    --recursive: Recursively organize sub-directories

    --model: Model to use as per platform
    """

    pipeline = PipelineCreator.create(
        {
            "path": path,
            "platform": platform,
            "api_key": api_key,
            "one_shot": one_shot,
            "recursive": recursive,
            "model": model,
        }
    )

    pipeline.run()


if __name__ == "__main__":
    app()
