import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from video_gen.providers import JimengProvider, TaskStatus

app = typer.Typer(name="task", help="Manage video generation tasks")
console = Console()


@app.command("status")
def task_status(
    task_id: str = typer.Argument(..., help="Task ID to check status for"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Continuously watch task status"),
    interval: float = typer.Option(2.0, "--interval", "-i", help="Watch interval in seconds"),
) -> None:
    provider = JimengProvider()
    
    async def check_status() -> TaskStatus:
        try:
            return await provider.check_status(task_id)
        except Exception as e:
            console.print(f"[red]Error checking status: {e}[/red]")
            raise typer.Exit(1)
    
    async def watch_status():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking task status...", total=None)
            
            while True:
                status = await check_status()
                status_display = _format_status(status)
                progress.update(task, description=f"Task {task_id}: {status_display}")
                
                if status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED):
                    break
                
                await asyncio.sleep(interval)
    
    async def single_check():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking task status...", total=None)
            status = await check_status()
            progress.update(task, description=f"Task {task_id}")
        
        console.print(f"\nStatus: {_format_status(status)}")
        
        table = Table(title="Task Details")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Task ID", task_id)
        table.add_row("Status", _format_status(status))
        
        console.print(table)
    
    if watch:
        asyncio.run(watch_status())
    else:
        asyncio.run(single_check())


def _format_status(status: TaskStatus) -> str:
    status_styles = {
        TaskStatus.PENDING: "[yellow]PENDING[/yellow]",
        TaskStatus.RUNNING: "[blue]RUNNING[/blue]",
        TaskStatus.SUCCEEDED: "[green]SUCCEEDED[/green]",
        TaskStatus.FAILED: "[red]FAILED[/red]",
        TaskStatus.UNKNOWN: "[dim]UNKNOWN[/dim]",
    }
    return status_styles.get(status, str(status.value))


@app.command("download")
def download_video(
    task_id: str = typer.Argument(..., help="Task ID to download video for"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    output_dir: Path = typer.Option(Path.cwd() / "output", "--output-dir", "-d", help="Output directory"),
) -> None:
    import httpx
    
    async def do_download():
        provider = JimengProvider()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            check_task = progress.add_task("Checking task status...", total=None)
            status = await provider.check_status(task_id)
            
            if status != TaskStatus.SUCCEEDED:
                progress.stop()
                console.print(f"[red]Task is not completed. Current status: {_format_status(status)}[/red]")
                raise typer.Exit(1)
            
            progress.update(check_task, description="Getting video URL...")
            
        console.print(f"[green]Task {task_id} completed. Downloading video...[/green]")
        
        video_url = f"https://api.jimeng.ai/video/{task_id}"
        
        if output:
            output_path = output
        else:
            output_path = output_dir / f"{task_id}.mp4"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(video_url, follow_redirects=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get("content-length", 0))
                
                with open(output_path, "wb") as f:
                    if total_size > 0:
                        with Progress(console=console) as progress:
                            download_task = progress.add_task("Downloading...", total=total_size)
                            for chunk in response.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                progress.update(download_task, advance=len(chunk))
                    else:
                        f.write(response.content)
            
            console.print(f"[green]Video downloaded to: {output_path}[/green]")
            
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Download failed: HTTP {e.response.status_code}[/red]")
            raise typer.Exit(1)
        except httpx.RequestError as e:
            console.print(f"[red]Download failed: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(do_download())


@app.command("cancel")
def cancel_task(
    task_id: str = typer.Argument(..., help="Task ID to cancel"),
) -> None:
    console.print("[yellow]Task cancellation is not yet implemented by the provider.[/yellow]")
    console.print(f"Task ID: {task_id}")
    raise typer.Exit(1)