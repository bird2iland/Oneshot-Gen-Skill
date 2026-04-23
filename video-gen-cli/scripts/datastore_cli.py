#!/usr/bin/env python3
"""CLI wrapper for DataStore operations."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_gen.core.data_store import DataStore, PresetData, CredentialData, ConfigData


def get_datastore() -> DataStore:
    return DataStore()


def get_presets(dimension: Optional[str] = None) -> list[dict[str, Any]]:
    store = get_datastore()
    presets = store.list_presets(dimension)
    return [
        {
            "id": p.id,
            "dimension": p.dimension,
            "name": p.name,
            "description": p.description,
            "keywords": p.keywords,
            "template": p.template,
            "metadata": p.metadata,
            "is_custom": p.is_custom,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        for p in presets
    ]


def save_preset(
    dimension: str,
    preset_id: str,
    name: str,
    description: str = "",
    keywords: Optional[list[str]] = None,
    template: str = "",
    metadata: Optional[dict[str, Any]] = None,
) -> bool:
    store = get_datastore()
    preset = PresetData(
        id=preset_id,
        dimension=dimension,
        name=name,
        description=description,
        keywords=keywords or [],
        template=template,
        metadata=metadata or {},
        is_custom=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    return store.save_preset(preset)


def delete_preset(dimension: str, preset_id: str) -> bool:
    store = get_datastore()
    return store.delete_preset(dimension, preset_id)


def save_preset_combo(
    name: str,
    visual: Optional[str] = None,
    time: Optional[str] = None,
    camera: Optional[str] = None,
) -> bool:
    """Save a preset combination."""
    store = get_datastore()
    return store.save_preset_combo(name, visual, time, camera)


def delete_preset_combo(name: str) -> bool:
    """Delete a preset combination."""
    store = get_datastore()
    return store.delete_preset_combo(name)


def get_preset_combos() -> list[dict[str, Any]]:
    """Get all preset combinations."""
    store = get_datastore()
    combos = store.list_preset_combos()
    return [
        {
            "name": p.name,
            "visual": p.metadata.get("visual"),
            "time": p.metadata.get("time"),
            "camera": p.metadata.get("camera"),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in combos
    ]


def save_credential(provider: str, api_key: str) -> bool:
    store = get_datastore()
    credential = CredentialData(
        provider=provider,
        api_key=api_key,
        metadata={},
        created_at=datetime.now(),
    )
    return store.save_credential(credential)


def get_credentials() -> list[dict[str, Any]]:
    store = get_datastore()
    providers = ["jimeng", "kling", "veo"]
    credentials = []
    
    for provider in providers:
        cred = store.get_credential(provider)
        if cred:
            credentials.append({
                "provider": cred.provider,
                "api_key": cred.api_key,
                "configured": True,
                "created_at": cred.created_at.isoformat() if cred.created_at else None,
            })
        else:
            credentials.append({
                "provider": provider,
                "api_key": "",
                "configured": False,
                "created_at": None,
            })
    
    return credentials


def delete_credential(provider: str) -> bool:
    store = get_datastore()
    return store.delete_credential(provider)


def get_config() -> dict[str, Any]:
    store = get_datastore()
    config = store.get_config()
    return {
        "output_dir": str(config.output_dir),
        "default_provider": config.default_provider,
        "default_model": config.default_model,
        "default_visual_preset": config.default_visual_preset,
        "default_time_preset": config.default_time_preset,
        "default_camera_preset": config.default_camera_preset,
        "default_duration": config.default_duration,
        "default_ratio": config.default_ratio,
        "default_mode": config.default_mode,
        "poll_interval": config.poll_interval,
        "poll_max_wait": config.poll_max_wait,
        "poll_retry_count": config.poll_retry_count,
        "verbose": config.verbose,
    }


def save_config(config_json: str) -> bool:
    store = get_datastore()
    data = json.loads(config_json)
    
    config = ConfigData(
        output_dir=Path(data.get("output_dir", "./output")),
        default_provider=data.get("default_provider", "jimeng"),
        default_model=data.get("default_model", "seedance2.0"),
        default_visual_preset=data.get("default_visual_preset"),
        default_time_preset=data.get("default_time_preset"),
        default_camera_preset=data.get("default_camera_preset"),
        default_duration=data.get("default_duration", 5),
        default_ratio=data.get("default_ratio", "16:9"),
        default_mode=data.get("default_mode", "fast"),
        poll_interval=data.get("poll_interval", 2.0),
        poll_max_wait=data.get("poll_max_wait", 300.0),
        poll_retry_count=data.get("poll_retry_count", 3),
        verbose=data.get("verbose", False),
    )
    
    return store.save_config(config)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        result = None
        
        if command == "get_presets":
            dimension = sys.argv[2] if len(sys.argv) > 2 else None
            result = get_presets(dimension)
        
        elif command == "save_preset":
            if len(sys.argv) < 5:
                raise ValueError("Usage: save_preset <dimension> <id> <name> [description] [keywords_json] [template] [metadata_json]")
            dimension = sys.argv[2]
            preset_id = sys.argv[3]
            name = sys.argv[4]
            description = sys.argv[5] if len(sys.argv) > 5 else ""
            keywords = json.loads(sys.argv[6]) if len(sys.argv) > 6 else []
            template = sys.argv[7] if len(sys.argv) > 7 else ""
            metadata = json.loads(sys.argv[8]) if len(sys.argv) > 8 else {}
            result = save_preset(dimension, preset_id, name, description, keywords, template, metadata)
        
        elif command == "delete_preset":
            if len(sys.argv) < 4:
                raise ValueError("Usage: delete_preset <dimension> <preset_id>")
            dimension = sys.argv[2]
            preset_id = sys.argv[3]
            result = delete_preset(dimension, preset_id)
        
        elif command == "save_preset_combo":
            if len(sys.argv) < 3:
                raise ValueError("Usage: save_preset_combo <name> [visual] [time] [camera]")
            name = sys.argv[2]
            visual = sys.argv[3] if len(sys.argv) > 3 else None
            time = sys.argv[4] if len(sys.argv) > 4 else None
            camera = sys.argv[5] if len(sys.argv) > 5 else None
            result = save_preset_combo(name, visual, time, camera)
        
        elif command == "delete_preset_combo":
            if len(sys.argv) < 3:
                raise ValueError("Usage: delete_preset_combo <name>")
            name = sys.argv[2]
            result = delete_preset_combo(name)
        
        elif command == "get_preset_combos":
            result = get_preset_combos()
        
        elif command == "save_credential":
            if len(sys.argv) < 4:
                raise ValueError("Usage: save_credential <provider> <api_key>")
            provider = sys.argv[2]
            api_key = sys.argv[3]
            result = save_credential(provider, api_key)
        
        elif command == "get_credentials":
            result = get_credentials()
        
        elif command == "delete_credential":
            if len(sys.argv) < 3:
                raise ValueError("Usage: delete_credential <provider>")
            provider = sys.argv[2]
            result = delete_credential(provider)
        
        elif command == "get_config":
            result = get_config()
        
        elif command == "save_config":
            if len(sys.argv) < 3:
                raise ValueError("Usage: save_config <config_json>")
            config_json = sys.argv[2]
            result = save_config(config_json)
        
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result))
    
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()