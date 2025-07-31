"""CLI for geekpedia_util tool."""

import sys
from typing import Optional

import typer
from loguru import logger
from typing_extensions import Annotated

LOG_LEVELS = ["WARNING", "INFO", "DEBUG", "TRACE"]

app = typer.Typer()


def version_callback(value: bool):
    """Print version information and exit."""
    from . import __version__

    if value:
        typer.echo(f"Version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, max=3, clamp=True)] = 0,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    quite: Annotated[bool, typer.Option("--quite", "-q", help="Suppress log messages")] = False,
) -> None:
    """Entry point for the geekpedia_util tool."""
    logger.remove(0)  # Remove default configuration
    
    if not quite:
        logger.add(
            sys.stderr,
            format="<level>{level: <8}</level> | <level>{message}</level>",
            level=LOG_LEVELS[verbose],
            backtrace=False,
            diagnose=True,
        )
    
    exit_code = 0

    try:
        print("Hello World from cc_test_3!")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt Received")

    except Exception:
        exit_code = 1
        logger.opt(exception=sys.exc_info()).critical("Unhandled Exception")

    finally:
        logger.info("Finally block - Exiting program")
        sys.exit(exit_code)  # Set exit code for shell tests.
        