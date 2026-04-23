from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from video_gen.cli.config import Config
from video_gen.core.types import OptimizationMode, PresetDimension
from video_gen.presets import PresetRegistry, register_default_presets
from video_gen.presets.base import BasePreset

console = Console()


@dataclass
class InteractiveState:
    visual_preset: Optional[str] = None
    time_preset: Optional[str] = None
    images: list[str] = field(default_factory=list)
    description: str = ""
    mode: OptimizationMode = OptimizationMode.FAST
    current_step: int = 0
    history: list[int] = field(default_factory=list)


class InteractiveGenerator:
    TOTAL_STEPS = 5

    def __init__(self, config: Optional[Config] = None):
        self._config = config or Config.load()
        self._registry = PresetRegistry()
        register_default_presets()
        self._state = InteractiveState()
        self._step_handlers: dict[int, Callable[[], str]] = {
            0: self._step_visual_style,
            1: self._step_time_sampling,
            2: self._step_upload_images,
            3: self._step_description,
            4: self._step_confirm,
        }

    def run(self) -> Optional[dict[str, Any]]:
        console.print(
            Panel("[bold cyan]Interactive Video Generation[/bold cyan]", expand=False)
        )
        console.print("[dim]Use Enter to skip, 'back' to go to previous step[/dim]\n")

        while self._state.current_step < self.TOTAL_STEPS:
            result = self._step_handlers[self._state.current_step]()

            if result == "back":
                if self._state.history:
                    self._state.current_step = self._state.history.pop()
                continue
            elif result == "skip":
                self._state.history.append(self._state.current_step)
                self._state.current_step += 1
                continue
            elif result == "done":
                return self._build_result()
            else:
                self._state.history.append(self._state.current_step)
                self._state.current_step += 1

        return self._build_result()

    def _step_visual_style(self) -> str:
        presets = self._registry.list(PresetDimension.VISUAL)
        return self._select_preset(
            step_num=1,
            title="选择视觉风格预设",
            presets=presets,
            state_attr="visual_preset",
        )

    def _step_time_sampling(self) -> str:
        presets = self._registry.list(PresetDimension.TIME)
        return self._select_preset(
            step_num=2,
            title="选择时间采样预设",
            presets=presets,
            state_attr="time_preset",
        )

    def _select_preset(
        self,
        step_num: int,
        title: str,
        presets: list[BasePreset],
        state_attr: str,
    ) -> str:
        console.print(f"\n[bold cyan]Step {step_num}: {title}[/bold cyan]")

        table = Table(show_header=True, header_style="bold")
        table.add_column("No.", style="dim", width=4)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")

        for idx, preset in enumerate(presets, 1):
            desc = preset.config.description
            display_desc = desc[:40] + "..." if len(desc) > 40 else desc
            table.add_row(
                str(idx),
                preset.config.id,
                preset.config.name,
                display_desc,
            )

        console.print(table)

        current_value = getattr(self._state, state_attr)
        if current_value:
            console.print(f"[dim]Current: {current_value}[/dim]")

        prompt_text = f"请选择 (1-{len(presets)}, 回车跳过, 'back' 返回)"
        response = Prompt.ask(prompt_text, default="")

        if response.lower() == "back":
            return "back"

        if response == "":
            return "skip"

        try:
            idx = int(response)
            if 1 <= idx <= len(presets):
                selected = presets[idx - 1]
                setattr(self._state, state_attr, selected.config.id)
                console.print(f"[green]已选择: {selected.config.name}[/green]")
                return "next"
            else:
                console.print("[red]无效选择，请重新输入[/red]")
                return self._select_preset(step_num, title, presets, state_attr)
        except ValueError:
            console.print("[red]无效输入，请重新输入[/red]")
            return self._select_preset(step_num, title, presets, state_attr)

    def _step_upload_images(self) -> str:
        console.print("\n[bold cyan]Step 3: 上传参考图[/bold cyan]")
        console.print("[dim]输入图片路径，多个路径用逗号分隔[/dim]")

        if self._state.images:
            console.print(f"[dim]Current: {', '.join(self._state.images)}[/dim]")

        response = Prompt.ask("图片路径 (回车跳过, 'back' 返回)", default="")

        if response.lower() == "back":
            return "back"

        if response == "":
            return "skip"

        paths = [p.strip() for p in response.split(",") if p.strip()]
        valid_paths = []
        invalid_paths = []

        for path in paths:
            if Path(path).exists():
                valid_paths.append(path)
            else:
                invalid_paths.append(path)

        if invalid_paths:
            console.print(f"[red]以下路径不存在: {', '.join(invalid_paths)}[/red]")
            retry = Prompt.ask("是否重新输入? (y/n)", default="y")
            if retry.lower() == "y":
                return self._step_upload_images()

        if valid_paths:
            self._state.images = valid_paths
            console.print(f"[green]已添加 {len(valid_paths)} 张图片[/green]")

        return "next"

    def _step_description(self) -> str:
        console.print("\n[bold cyan]Step 4: 输入描述[/bold cyan]")
        console.print("[dim]输入视频生成的描述/提示词[/dim]")

        if self._state.description:
            console.print(f"[dim]Current: {self._state.description[:50]}...[/dim]")

        response = Prompt.ask("描述 (回车跳过, 'back' 返回)", default="")

        if response.lower() == "back":
            return "back"

        if response == "":
            return "skip"

        self._state.description = response
        console.print("[green]描述已设置[/green]")
        return "next"

    def _step_confirm(self) -> str:
        console.print("\n[bold cyan]Step 5: 确认参数[/bold cyan]")

        table = Table(title="Generation Parameters", show_header=True)
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")

        NOT_SET = "[dim]Not set[/dim]"
        table.add_row("Visual Style", self._state.visual_preset or NOT_SET)
        table.add_row("Time Sampling", self._state.time_preset or NOT_SET)
        images_display = (
            ", ".join(self._state.images) if self._state.images else NOT_SET
        )
        table.add_row("Images", images_display)
        table.add_row("Description", self._state.description or NOT_SET)
        table.add_row("Mode", self._state.mode.value)

        console.print(table)

        if not self._state.images:
            console.print(
                "[yellow]Warning: No images specified. Generation may fail.[/yellow]"
            )

        response = Prompt.ask(
            "\n确认生成? (y/n, 'back' 返回, 'edit' 编辑)", default="y"
        )

        if response.lower() == "back":
            return "back"

        if response.lower() == "edit":
            return self._edit_params()

        if response.lower() in ("y", "yes"):
            return "done"

        console.print("[red]已取消生成[/red]")
        return "cancel"

    def _edit_params(self) -> str:
        console.print("\n[dim]选择要编辑的参数:[/dim]")
        console.print("  [1] Visual Style")
        console.print("  [2] Time Sampling")
        console.print("  [3] Images")
        console.print("  [4] Description")
        console.print("  [5] Mode (fast/quality)")

        response = Prompt.ask("选择 (1-5)", default="")

        edit_map = {
            "1": 0,
            "2": 1,
            "3": 2,
            "4": 3,
            "5": -1,
        }

        if response in edit_map:
            if response == "5":
                mode_str = Prompt.ask(
                    "Mode (fast/quality)", default=self._state.mode.value
                )
                new_mode = (
                    OptimizationMode.QUALITY
                    if mode_str.lower() == "quality"
                    else OptimizationMode.FAST
                )
                self._state.mode = new_mode
                console.print(
                    f"[green]Mode set to: {self._state.mode.value}[/green]"
                )
                return self._step_confirm()
            else:
                self._state.current_step = edit_map[response]
                return "next"

        console.print("[red]无效选择[/red]")
        return self._step_confirm()

    def _build_result(self) -> dict[str, Any]:
        return {
            "visual": self._state.visual_preset,
            "time": self._state.time_preset,
            "images": self._state.images,
            "description": self._state.description,
            "mode": self._state.mode,
        }
