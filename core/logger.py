from __future__ import annotations

import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table


class Logger:
    _instance: Optional[Logger] = None

    def __init__(self, verbose: bool = False, name: str = "domainhunter") -> None:
        self.console = Console(force_terminal=True)
        self.verbose = verbose
        self._progress: Optional[Progress] = None

        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True, show_path=False)],
        )
        self.logger = logging.getLogger(name)

    @classmethod
    def get(cls, verbose: bool = False) -> Logger:
        if cls._instance is None:
            cls._instance = cls(verbose=verbose)
        return cls._instance

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def success(self, message: str) -> None:
        self.console.print(f"[bold green]✓[/] {message}")

    def fail(self, message: str) -> None:
        self.console.print(f"[bold red]✗[/] {message}")

    def print_table(self, title: str, columns: list[str], rows: list[list[str]]) -> None:
        table = Table(title=title, title_style="bold cyan")
        for col in columns:
            table.add_column(col, style="cyan" if col == columns[0] else "white")
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def progress_bar(self, description: str, total: int) -> Progress:
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        )
        self._progress.start()
        self._progress.add_task(description, total=total)
        return self._progress

    def stop_progress(self) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None

    def section(self, title: str) -> None:
        self.console.print(f"\n[bold cyan]--- {title} ---[/]")
