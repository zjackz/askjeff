from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from app.config import settings


@dataclass
class ImportConfig:
    sheet_name: str = "产品详情"
    required_fields: list[str] = field(default_factory=lambda: ["asin", "title", "currency"])
    on_missing_required: str = "skip"
    column_aliases: dict[str, str] = field(default_factory=dict)
    normalization: dict[str, Any] = field(default_factory=dict)

    def merge_overrides(
        self,
        *,
        sheet_name: str | None = None,
        on_missing_required: str | None = None,
        column_aliases: dict[str, str] | None = None,
    ) -> "ImportConfig":
        cfg = ImportConfig(
            sheet_name=sheet_name or self.sheet_name,
            required_fields=list(self.required_fields),
            on_missing_required=on_missing_required or self.on_missing_required,
            column_aliases=dict(self.column_aliases),
            normalization=dict(self.normalization),
        )
        if column_aliases:
            cfg.column_aliases.update(column_aliases)
        return cfg


def load_import_config() -> ImportConfig:
    """加载导入映射配置，优先读取 import_mapping.yaml，否则回退示例文件。"""
    config_dir = settings.storage_dir.parent / "config"
    config_path = config_dir / "import_mapping.yaml"
    fallback_path = config_dir / "import_mapping.example.yaml"
    path = config_path if config_path.exists() else fallback_path
    if not path.exists():
        return ImportConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ImportConfig(
        sheet_name=data.get("sheet_name", "产品详情"),
        required_fields=data.get("required_fields", ["asin", "title", "currency"]),
        on_missing_required=data.get("on_missing_required", "skip"),
        column_aliases=data.get("column_aliases", {}) or {},
        normalization=data.get("normalization", {}) or {},
    )
