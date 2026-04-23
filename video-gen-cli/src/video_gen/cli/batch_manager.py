from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from video_gen.cli.config import Config
from video_gen.core.batch_engine import (
    BatchEngine,
    BatchRequest,
    BatchResult,
    ProgressInfo,
)
from video_gen.core.engine import Config as EngineConfig


console = Console()


class BatchManager:
    def __init__(self, config: Optional[Config] = None):
        self._config = config or Config()
        engine_config = EngineConfig(output_dir=self._config.output_dir)
        self._engine = BatchEngine(config=engine_config)

    def load_batch_request(self, yaml_path: Path) -> BatchRequest:
        return self._engine.from_yaml(yaml_path)

    async def execute_batch(
        self,
        request: BatchRequest,
        verbose: bool = False,
    ) -> BatchResult:
        progress_data = {"current": 0, "succeeded": 0, "failed": 0}

        def progress_callback(info: ProgressInfo) -> None:
            progress_data["current"] = info.completed
            progress_data["succeeded"] = info.succeeded
            progress_data["failed"] = info.failed

            if verbose:
                console.print(
                    f"[dim]Task {info.current_index + 1}/{info.total}: "
                    f"{info.current_description[:50]}...[/dim]"
                )

        result = await self._engine.execute_batch(
            request=request,
            progress_callback=progress_callback,
        )

        return result

    def display_result(self, result: BatchResult, verbose: bool = False) -> None:
        console.print()

        if result.success:
            console.print(Panel(
                f"[green bold]All tasks completed successfully![/green bold]\n\n"
                f"[cyan]Total:[/cyan] {result.total}\n"
                f"[cyan]Duration:[/cyan] {result.duration:.2f}s",
                title="[green]Batch Complete[/green]",
                border_style="green",
            ))
        else:
            console.print(Panel(
                f"[yellow bold]Batch completed with errors[/yellow bold]\n\n"
                f"[cyan]Total:[/cyan] {result.total}\n"
                f"[green]Succeeded:[/green] {result.succeeded}\n"
                f"[red]Failed:[/red] {result.failed}\n"
                f"[cyan]Duration:[/cyan] {result.duration:.2f}s",
                title="[yellow]Batch Complete[/yellow]",
                border_style="yellow",
            ))

        if verbose or not result.success:
            table = Table(title="Task Results")
            table.add_column("#", style="cyan", width=4)
            table.add_column("Status", style="white", width=10)
            table.add_column("Video Path", style="green")
            table.add_column("Error", style="red")

            for task_result in result.results:
                success_mark = "[green]✓[/green]"
                fail_mark = "[red]✗[/red]"
                status = success_mark if task_result.success else fail_mark
                video = task_result.video_path or "-"
                error = task_result.error or "-"

                if len(video) > 40:
                    video = "..." + video[-37:]
                if len(error) > 40:
                    error = error[:37] + "..."

                table.add_row(
                    str(task_result.index + 1),
                    status,
                    video,
                    error if not task_result.success else "-",
                )

            console.print(table)

    def display_progress_during_execution(self, total: int) -> None:
        console.print("\n[cyan]Starting batch processing...[/cyan]")
        console.print(f"[dim]Total tasks: {total}[/dim]\n")