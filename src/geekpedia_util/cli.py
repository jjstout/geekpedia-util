"""CLI for geekpedia_util tool."""
import sys
from pathlib import Path
from typing import Optional

import typer
import yaml

from loguru import logger
from typing_extensions import Annotated

from .services import get_new_item
from .utils import slugify, wrap_text

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
    uri: Annotated[str, typer.Argument(help="URI of the article to process")],
    verbose: Annotated[int, typer.Option("--verbose", "-v", count=True, max=3, clamp=True)] = 0,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    quite: Annotated[bool, typer.Option("--quite", "-q", help="Suppress log messages")] = False,
    dst_dir: Annotated[Path, typer.Option("--dst-dir", "-d", help="Output directory for results")] = Path("_refs/articles"),
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
        meta, body = get_new_item(uri)
        
        dst_path = dst_dir / f"{slugify(meta['cite_title'])}.txt"
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        with dst_path.open("w", encoding="utf-8") as fd_out:
            fd_out.write("---\n")
            yaml.dump(meta, fd_out, allow_unicode=True, sort_keys=False)
            fd_out.write("---\n\n")
            fd_out.write(wrap_text(body, width=80))

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt Received")

    except Exception:
        exit_code = 1
        logger.opt(exception=sys.exc_info()).critical("Unhandled Exception")

    finally:
        logger.info("Finally block - Exiting program")
        sys.exit(exit_code)  # Set exit code for shell tests.
        