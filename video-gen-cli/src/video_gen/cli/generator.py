import asyncio
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

from video_gen.core.types import GenerationRequest, GenerationResult, OptimizationMode, PollConfig
from video_gen.presets import PresetRegistry, register_default_presets
from video_gen.presets.composer import PresetComposer
from video_gen.presets.validator import PresetCombinationValidator
from video_gen.optimizers import create_optimizer
from video_gen.providers import JimengProvider, JimengStatusChecker
from video_gen.cli.config import Config

console = Console()


class VideoGenerator:
    def __init__(self, config: Optional[Config] = None):
        self._config = config or Config.load()
        self._registry = PresetRegistry()
        register_default_presets()
        self._composer = PresetComposer(self._registry)
        self._provider = JimengProvider()

    async def generate(
        self,
        images: list[str],
        visual: Optional[str] = None,
        time: Optional[str] = None,
        camera: Optional[str] = None,
        description: str = "",
        mode: OptimizationMode = OptimizationMode.FAST,
        provider: str = "jimeng",
        output_dir: Optional[Path] = None,
        verbose: bool = False,
    ) -> GenerationResult:
        validator = PresetCombinationValidator(visual, time, camera)
        warnings = await validator.validate()
        
        if warnings:
            console.print("[yellow]Preset combination warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  ⚠ {warning}")
            console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Composing prompt...", total=100)
            
            progress.update(task, advance=10, description="Building prompt from presets...")
            composed_prompt = await self._composer.compose(visual, time, camera, description)
            
            progress.update(task, advance=20, description="Optimizing prompt...")
            optimized_prompt = await self._optimize_prompt(composed_prompt, mode)
            
            if verbose:
                console.print(Panel(f"[dim]Original:[/dim] {description}\n[dim]Composed:[/dim] {composed_prompt}\n[dim]Optimized:[/dim] {optimized_prompt}", title="Prompt"))
            
            progress.update(task, advance=30, description="Preparing generation request...")
            request = GenerationRequest(
                images=images,
                visual_preset=visual,
                time_preset=time,
                camera_preset=camera,
                description=optimized_prompt,
                mode=mode,
                provider=provider,
                duration=self._config.default_duration,
                ratio=self._config.default_ratio,
                model=self._config.default_model,
                poll_config=PollConfig(
                    interval=self._config.poll_interval,
                    max_wait=self._config.poll_max_wait,
                    retry_count=self._config.poll_retry_count,
                ),
            )
            
            from video_gen.providers.base import GenerationConfig
            gen_config = GenerationConfig(
                images=images,
                prompt=optimized_prompt,
                duration=request.duration,
                ratio=request.ratio,
                model=request.model,
                output_dir=output_dir or self._config.output_dir,
            )
            
            progress.update(task, advance=20, description="Starting video generation...")
            result = await self._provider.generate(gen_config)
            
            progress.update(task, advance=20, description="Processing result...")
            
            if result.success:
                progress.update(task, advance=100, description="Generation completed!")
            else:
                progress.stop()
                self._display_error(result)
                return result
            
            return result

    async def _optimize_prompt(self, prompt: str, mode: OptimizationMode) -> str:
        optimizer = create_optimizer(mode=mode)
        return await optimizer.optimize(prompt)

    def _display_error(self, result: GenerationResult) -> None:
        console.print()
        console.print(Panel(
            f"[red bold]Error Code:[/red bold] {result.error_code or 'UNKNOWN'}\n\n"
            f"[red]Message:[/red] {result.error or 'Unknown error occurred'}\n\n"
            f"[yellow]Suggestion:[/yellow] {result.suggestion or 'Please try again'}",
            title="[red]Generation Failed[/red]",
            border_style="red",
        ))

    async def check_status(self) -> dict:
        checker = JimengStatusChecker()
        status = await checker.check_full_status()
        return {
            "installed": status.installed,
            "version": status.version,
            "logged_in": status.logged_in,
            "user_info": status.user_info,
            "error": status.error,
        }