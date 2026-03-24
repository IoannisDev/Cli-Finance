"""Console script for cli_finance."""

import typer
from rich.console import Console

from cli_finance import utils

app = typer.Typer()
console = Console()


@app.command()
def main() -> None:
    """Console script for cli_finance."""
    console.print("Replace this message by putting your code into cli_finance.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
