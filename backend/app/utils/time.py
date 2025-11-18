from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """统一提供带时区的当前时间，便于替换 utcnow()。"""
    return datetime.now(timezone.utc)
