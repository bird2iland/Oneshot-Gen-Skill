from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from video_gen.core.data_store import CredentialData, DataStore

app = typer.Typer(name="credential", help="Manage credentials for providers and LLM")
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


def _mask_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "****"
    return api_key[:4] + "****" + api_key[-4:]


@app.command("set")
def set_credential(
    provider: str = typer.Argument(..., help="Provider name (jimeng/kling)"),
    api_key: str = typer.Option(..., "--api-key", "-k", help="API key for the provider"),
) -> None:
    data_store = get_data_store()
    
    credential = CredentialData(
        provider=provider.lower(),
        api_key=api_key,
        created_at=datetime.now(),
    )
    
    result = data_store.save_credential(credential)
    if result:
        console.print(f"[green]Credential for '{provider}' saved successfully[/green]")
    else:
        console.print(f"[red]Failed to save credential for '{provider}'[/red]")
        raise typer.Exit(1)


@app.command("get")
def get_credential(
    provider: str = typer.Argument(..., help="Provider name (jimeng/kling)"),
) -> None:
    data_store = get_data_store()
    
    credential = data_store.get_credential(provider.lower())
    if not credential:
        console.print(f"[yellow]No credential found for '{provider}'[/yellow]")
        raise typer.Exit(1)
    
    table = Table(title=f"Credentials for '{provider}'")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Provider", credential.provider)
    table.add_row("API Key", _mask_api_key(credential.api_key))
    
    if credential.created_at:
        table.add_row("Created At", credential.created_at.isoformat())
    
    console.print(table)


@app.command("delete")
def delete_credential(
    provider: str = typer.Argument(..., help="Provider name (jimeng/kling)"),
) -> None:
    data_store = get_data_store()
    
    credential = data_store.get_credential(provider.lower())
    if not credential:
        console.print(f"[yellow]No credential found for '{provider}'[/yellow]")
        raise typer.Exit(1)
    
    result = data_store.delete_credential(provider.lower())
    if result:
        console.print(f"[green]Credential for '{provider}' deleted successfully[/green]")
    else:
        console.print(f"[red]Failed to delete credential for '{provider}'[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_credentials() -> None:
    data_store = get_data_store()
    
    table = Table(title="All Credentials")
    table.add_column("Provider", style="cyan")
    table.add_column("API Key", style="green")
    table.add_column("Created At", style="yellow")
    
    known_providers = ["jimeng", "kling"]
    found_any = False
    
    for provider in known_providers:
        credential = data_store.get_credential(provider)
        if credential:
            found_any = True
            created_str = credential.created_at.isoformat() if credential.created_at else "-"
            table.add_row(
                credential.provider,
                _mask_api_key(credential.api_key),
                created_str,
            )
    
    llm_config = data_store.get_llm_config()
    if llm_config and llm_config.get("api_key"):
        found_any = True
        provider_info = llm_config.get("provider", "openai")
        table.add_row(
            f"llm ({provider_info})",
            _mask_api_key(llm_config["api_key"]),
            "-",
        )
    
    if not found_any:
        console.print("[yellow]No credentials configured[/yellow]")
    else:
        console.print(table)