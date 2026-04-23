import asyncio
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from video_gen.core.data_store import DataStore, PresetData
from video_gen.presets.validator import PresetCombinationValidator

app = typer.Typer(name="preset", help="Manage presets for video generation")
console = Console()

_data_store: Optional[DataStore] = None


def set_data_store(data_store: DataStore) -> None:
    global _data_store
    _data_store = data_store


def get_data_store() -> DataStore:
    global _data_store
    if _data_store is None:
        _data_store = DataStore()
    return _data_store


@app.command("list")
def list_presets(
    dimension: Optional[str] = typer.Option(None, "--dimension", "-d", help="Filter by dimension (visual/time/camera)"),
) -> None:
    data_store = get_data_store()
    
    if dimension:
        valid_dimensions = ["visual", "time", "camera"]
        if dimension.lower() not in valid_dimensions:
            console.print(f"[red]Invalid dimension: {dimension}. Valid options: visual, time, camera[/red]")
            raise typer.Exit(1)
        presets = data_store.list_presets(dimension=dimension.lower())
        if presets:
            _display_presets_table(presets, dimension.capitalize())
    else:
        for dim in ["visual", "time", "camera"]:
            presets = data_store.list_presets(dimension=dim)
            if presets:
                _display_presets_table(presets, dim.capitalize())


def _display_presets_table(presets: list[PresetData], title: str) -> None:
    table = Table(title=f"{title} Presets")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    table.add_column("Keywords", style="yellow")
    table.add_column("Custom", style="magenta")
    
    for preset in presets:
        keywords = ", ".join(preset.keywords[:3])
        if len(preset.keywords) > 3:
            keywords += "..."
        table.add_row(
            preset.id,
            preset.name,
            preset.description[:50] + "..." if len(preset.description) > 50 else preset.description,
            keywords,
            "✓" if preset.is_custom else "",
        )
    
    console.print(table)
    console.print()


@app.command("show")
def show_preset(
    preset_id: str = typer.Argument(..., help="Preset ID to show details for"),
    dimension: Optional[str] = typer.Option(None, "--dimension", "-d", help="Preset dimension (visual/time/camera)"),
) -> None:
    data_store = get_data_store()
    
    if dimension:
        valid_dimensions = ["visual", "time", "camera"]
        if dimension.lower() not in valid_dimensions:
            console.print(f"[red]Invalid dimension: {dimension}. Valid options: visual, time, camera[/red]")
            raise typer.Exit(1)
        
        preset = data_store.get_preset(dimension.lower(), preset_id)
        if not preset:
            console.print(f"[red]Preset '{preset_id}' not found in {dimension}[/red]")
            raise typer.Exit(1)
        
        _display_preset_detail(preset)
    else:
        found = False
        for dim in ["visual", "time", "camera"]:
            preset = data_store.get_preset(dim, preset_id)
            if preset:
                console.print(f"[cyan]Found in {dim} dimension:[/cyan]")
                _display_preset_detail(preset)
                found = True
                break
        
        if not found:
            console.print(f"[red]Preset '{preset_id}' not found[/red]")
            raise typer.Exit(1)


def _display_preset_detail(preset: PresetData) -> None:
    console.print(Panel(f"[bold green]{preset.name}[/bold green]", expand=False))
    console.print(f"[cyan]ID:[/cyan] {preset.id}")
    console.print(f"[cyan]Dimension:[/cyan] {preset.dimension}")
    console.print(f"[cyan]Description:[/cyan] {preset.description}")
    
    if preset.keywords:
        console.print(f"[cyan]Keywords:[/cyan]")
        for kw in preset.keywords:
            console.print(f"  • {kw}")
    
    if preset.metadata:
        console.print(f"[cyan]Metadata:[/cyan]")
        for key, value in preset.metadata.items():
            console.print(f"  • {key}: {value}")


@app.command("save")
def save_preset(
    id: str = typer.Option(..., "--id", "-i", help="Preset ID"),
    dimension: str = typer.Option(..., "--dimension", "-d", help="Preset dimension (visual/time/camera)"),
    name: str = typer.Option(..., "--name", "-n", help="Preset name"),
    description: Optional[str] = typer.Option(None, "--description", "-D", help="Preset description"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Comma-separated keywords"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Prompt template"),
) -> None:
    valid_dimensions = ["visual", "time", "camera"]
    if dimension.lower() not in valid_dimensions:
        console.print(f"[red]Invalid dimension: {dimension}. Valid options: visual, time, camera[/red]")
        raise typer.Exit(1)
    
    data_store = get_data_store()
    
    existing = data_store.get_preset(dimension.lower(), id)
    if existing and not existing.is_custom:
        console.print(f"[red]Cannot overwrite built-in preset '{id}'[/red]")
        raise typer.Exit(1)
    
    keyword_list = []
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    preset = PresetData(
        id=id,
        dimension=dimension.lower(),
        name=name,
        description=description or f"Custom preset: {name}",
        keywords=keyword_list,
        template=template or "{description}",
        is_custom=True,
        created_at=existing.created_at if existing else datetime.now(),
        updated_at=datetime.now(),
    )
    
    result = data_store.save_preset(preset)
    if result:
        console.print(f"[green]Preset '{id}' saved successfully in {dimension} dimension[/green]")
    else:
        console.print(f"[red]Failed to save preset '{id}'[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_preset(
    id: str = typer.Argument(..., help="Preset ID to delete"),
    dimension: Optional[str] = typer.Option(None, "--dimension", "-d", help="Preset dimension (visual/time/camera)"),
) -> None:
    data_store = get_data_store()
    
    if dimension:
        valid_dimensions = ["visual", "time", "camera"]
        if dimension.lower() not in valid_dimensions:
            console.print(f"[red]Invalid dimension: {dimension}. Valid options: visual, time, camera[/red]")
            raise typer.Exit(1)
        
        preset = data_store.get_preset(dimension.lower(), id)
        if not preset:
            console.print(f"[red]Preset '{id}' not found in {dimension}[/red]")
            raise typer.Exit(1)
        
        if not preset.is_custom:
            console.print(f"[red]Cannot delete built-in preset '{id}'[/red]")
            raise typer.Exit(1)
        
        result = data_store.delete_preset(dimension.lower(), id)
        if result:
            console.print(f"[green]Preset '{id}' deleted successfully[/green]")
        else:
            console.print(f"[red]Failed to delete preset '{id}'[/red]")
            raise typer.Exit(1)
    else:
        found = False
        for dim in ["visual", "time", "camera"]:
            preset = data_store.get_preset(dim, id)
            if preset:
                if not preset.is_custom:
                    console.print(f"[red]Cannot delete built-in preset '{id}'[/red]")
                    raise typer.Exit(1)
                
                result = data_store.delete_preset(dim, id)
                if result:
                    console.print(f"[green]Preset '{id}' deleted successfully from {dim} dimension[/green]")
                    found = True
                break
        
        if not found:
            console.print(f"[red]Preset '{id}' not found[/red]")
            raise typer.Exit(1)