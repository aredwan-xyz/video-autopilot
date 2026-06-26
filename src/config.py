"""Load settings.yaml + channels.yaml + .env and expose a merged, per-channel config."""
from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROMPTS_DIR = CONFIG_DIR / "prompts"

load_dotenv(ROOT / ".env")


def _read_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_settings() -> dict:
    return _read_yaml(CONFIG_DIR / "settings.yaml")


def load_channels() -> dict:
    return _read_yaml(CONFIG_DIR / "channels.yaml").get("channels", {})


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def env(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def channel_config(channel_key: str) -> dict:
    """Merge global settings with a single channel's overrides into one flat-ish dict."""
    settings = load_settings()
    channels = load_channels()
    if channel_key not in channels:
        raise SystemExit(
            f"Channel '{channel_key}' not found. Available: {', '.join(channels) or '(none)'}"
        )
    cfg = deepcopy(settings)
    cfg["channel"] = deepcopy(channels[channel_key])
    cfg["channel"]["key"] = channel_key

    # Per-channel voice override flows into the active tts provider.
    voice = cfg["channel"].get("voice")
    if voice:
        cfg["tts"]["edge_voice"] = voice
        cfg["tts"]["elevenlabs_voice"] = cfg["channel"].get(
            "elevenlabs_voice", cfg["tts"].get("elevenlabs_voice")
        )
    if cfg["channel"].get("platforms"):
        cfg["publish"]["platforms"] = cfg["channel"]["platforms"]
    return cfg


def all_channel_keys() -> list[str]:
    return list(load_channels().keys())
