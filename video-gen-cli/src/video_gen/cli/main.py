import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from video_gen.cli.batch_manager import BatchManager
from video_gen.cli.config import Config, set_data_store
from video_gen.cli.credential_manager import app as credential_app, set_data_store as credential_set_data_store
from video_gen.cli.gen_interactive import InteractiveGenerator
from video_gen.cli.generator import VideoGenerator
from video_gen.cli.preset_manager import app as preset_app, set_data_store as preset_set_data_store
from video_gen.cli.task_manager import app as task_app
from video_gen.core.data_store import DataStore
from video_gen.core.types import OptimizationMode
from video_gen.presets import register_default_presets
from video_gen.providers import JimengStatusChecker

app = typer.Typer(
    name="video-gen",
    help="Video generation CLI tool with preset management",
    add_completion=False,
)
console = Console()

_data_store: Optional[DataStore] = None


def get_data_store() -> DataStore:
    global _data_store
    if _data_store is None:
        _data_store = DataStore()
    return _data_store


app.add_typer(preset_app, name="preset")
app.add_typer(credential_app, name="credential")
app.add_typer(task_app, name="task")


def _init_data_store() -> None:
    data_store = get_data_store()
    preset_set_data_store(data_store)
    credential_set_data_store(data_store)
    set_data_store(data_store)


def _display_error(code: str, message: str, suggestion: str) -> None:
    console.print()
    console.print(Panel(
        f"[red bold]Error Code:[/red bold] {code}\n\n"
        f"[red]Message:[/red] {message}\n\n"
        f"[yellow]Suggestion:[/yellow] {suggestion}",
        title="[red]Error[/red]",
        border_style="red",
    ))


@app.callback()
def main(
    check_status: bool = typer.Option(
        False,
        "--check-status",
        "-c",
        help="Check Jimeng CLI status on startup",
    ),
) -> None:
    register_default_presets()
    _init_data_store()
    if check_status:
        asyncio.run(_check_jimeng_status())


async def _check_jimeng_status() -> None:
    checker = JimengStatusChecker()
    status = await checker.check_full_status()

    table = Table(title="Jimeng CLI Status")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    table.add_row(
        "Installation",
        "[green]✓ Installed[/green]" if status.installed else "[red]✗ Not Installed[/red]",
        f"v{status.version}" if status.version else "-",
    )

    table.add_row(
        "Authentication",
        "[green]✓ Logged In[/green]" if status.logged_in else "[red]✗ Not Logged In[/red]",
        status.user_info or "-",
    )

    console.print(table)

    if not status.installed or not status.logged_in:
        console.print()
        console.print(Panel(checker.get_install_guide(), title="Setup Guide", border_style="yellow"))


@app.command()
def gen(
    visual: Optional[str] = typer.Option(None, "--visual", "-v", help="Visual style preset ID"),
    time: Optional[str] = typer.Option(None, "--time", "-t", help="Time sampling preset ID"),
    camera: Optional[str] = typer.Option(None, "--camera", "-c", help="Camera movement preset ID"),
    images: Optional[List[str]] = typer.Option(None, "--image", "-i", help="Image paths (can specify multiple)"),
    description: str = typer.Option("", "--description", "-d", help="Video description/prompt"),
    mode: str = typer.Option("fast", "--mode", "-m", help="Optimization mode (fast/quality)"),
    provider: str = typer.Option("jimeng", "--provider", "-p", help="Video generation provider"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Enable verbose output"),
    interactive: bool = typer.Option(False, "--interactive", "-I", help="Interactive step-by-step mode"),
) -> None:
    config = Config.load()

    if output is None:
        output = config.output_dir

    if interactive:
        interactive_gen = InteractiveGenerator(config)
        params = interactive_gen.run()

        if params is None:
            console.print("[yellow]Generation cancelled[/yellow]")
            raise typer.Exit(0)

        visual = params.get("visual") or visual
        time = params.get("time") or time
        images = params.get("images") or images
        description = params.get("description") or description
        mode = params.get("mode", OptimizationMode.FAST).value if params.get("mode") else mode

    if not images:
        console.print("[red]Error: At least one image is required (--image)[/red]")
        raise typer.Exit(1)

    for image_path in images:
        if not Path(image_path).exists():
            console.print(f"[red]Error: Image not found: {image_path}[/red]")
            raise typer.Exit(1)

    opt_mode = OptimizationMode.FAST
    if mode.lower() == "quality":
        opt_mode = OptimizationMode.QUALITY

    generator = VideoGenerator(config)

    try:
        result = asyncio.run(generator.generate(
            images=images,
            visual=visual,
            time=time,
            camera=camera,
            description=description,
            mode=opt_mode,
            provider=provider,
            output_dir=output,
            verbose=verbose,
        ))

        if result.success:
            console.print()
            console.print(Panel(
                f"[green bold]Video generated successfully![/green bold]\n\n"
                f"[cyan]Task ID:[/cyan] {result.task_id or 'N/A'}\n"
                f"[cyan]Video:[/cyan] {result.video_path or 'N/A'}",
                title="Success",
                border_style="green",
            ))
        else:
            _display_error(
                result.error_code or "GENERATION_FAILED",
                result.error or "Unknown error",
                result.suggestion or "Please try again",
            )
            raise typer.Exit(1)

    except Exception as e:
        _display_error("UNEXPECTED_ERROR", str(e), "An unexpected error occurred")
        raise typer.Exit(1)


@app.command()
def check() -> None:
    asyncio.run(_check_jimeng_status())


@app.command()
def batch(
    input: Path = typer.Option(..., "--input", "-i", help="Path to YAML batch configuration file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory (overrides YAML)"),
    concurrency: Optional[int] = typer.Option(None, "--concurrency", "-c", help="Max concurrent tasks"),
    continue_on_error: bool = typer.Option(True, "--continue-on-error/--stop-on-error", help="Continue on individual task failures"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Enable verbose output"),
) -> None:
    config = Config.load()

    if not input.exists():
        console.print(f"[red]Error: Batch config file not found: {input}[/red]")
        raise typer.Exit(1)

    manager = BatchManager(config)

    try:
        request = manager.load_batch_request(input)

        if output:
            request.output_dir = output
        if concurrency:
            request.concurrency = concurrency
        request.continue_on_error = continue_on_error

        if not request.tasks:
            console.print("[red]Error: No tasks defined in batch config[/red]")
            raise typer.Exit(1)

        console.print(f"\n[cyan]Loading batch configuration from:[/cyan] {input}")
        console.print(f"[cyan]Tasks:[/cyan] {len(request.tasks)}")
        console.print(f"[cyan]Concurrency:[/cyan] {request.concurrency}")
        console.print(f"[cyan]Mode:[/cyan] {request.mode.value}")
        console.print(f"[cyan]Provider:[/cyan] {request.provider}")

        result = asyncio.run(manager.execute_batch(
            request=request,
            verbose=verbose,
        ))

        manager.display_result(result, verbose=verbose)

        if not result.success:
            raise typer.Exit(1)

    except ValueError as e:
        _display_error("INVALID_CONFIG", str(e), "Please check your YAML configuration")
        raise typer.Exit(1)
    except Exception as e:
        _display_error("BATCH_ERROR", str(e), "An error occurred during batch processing")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Set default output directory"),
    default_provider: Optional[str] = typer.Option(None, "--default-provider", "-p", help="Set default provider"),
    default_model: Optional[str] = typer.Option(None, "--default-model", "-m", help="Set default model"),
    default_duration: Optional[int] = typer.Option(None, "--default-duration", "-d", help="Set default duration"),
    verbose: Optional[bool] = typer.Option(None, "--verbose/--no-verbose", help="Set verbose mode"),
) -> None:
    cfg = Config.load(get_data_store())

    if show or (not any([output_dir, default_provider, default_model, default_duration, verbose is not None])):
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        for key, value in cfg.to_dict().items():
            table.add_row(key, str(value))

        console.print(table)
        console.print(f"\n[dim]Config file: {get_data_store().CONFIG_FILE}[/dim]")
        return

    if output_dir:
        cfg.set_output_dir(output_dir)
    if default_provider:
        cfg.set_default_provider(default_provider)
    if default_model:
        cfg.set_default_model(default_model)
    if default_duration:
        cfg.set_default_duration(default_duration)
    if verbose is not None:
        cfg.set_verbose(verbose)

    cfg.save()
    console.print("[green]Configuration saved successfully[/green]")

    table = Table(title="Updated Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in cfg.to_dict().items():
        table.add_row(key, str(value))

    console.print(table)


if __name__ == "__main__":
    app()
