from rich.console import Console


def print_error(msg: str) -> None:
    err = Console(stderr=True)
    err.print(f"\n[bold red]ERROR: {msg}[/]\n")


def print_success(msg: str) -> None:
    success = Console(stderr=True)
    success.print(f"\n[bold green]{msg}[/]\n")
