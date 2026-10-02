import fire
import sys
from rich.console import Console

try:
    from src.RAGEngine import RAGEngine
    from src.utils.display import print_error
except ModuleNotFoundError:
    Console(stderr=True).print(
        "\n[bold red]ERROR:[/] Please run with 'uv run python -m src'\n")
    sys.exit(1)


def main() -> int:
    try:
        fire.Fire(RAGEngine)
        return 0
    except Exception as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_error("program interrupted")
        sys.exit(130)
