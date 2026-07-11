from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    radar_profile_path: Path = Path("config/profile.yaml")
    radar_sources_path: Path = Path("config/sources.yaml")
    radar_db_path: Path = Path(".data/radar.db")
    radar_output_dir: Path = Path("digests")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
