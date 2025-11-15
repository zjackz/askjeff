#!/usr/bin/env python3
"""统计导入/问答/导出指标并输出 CSV."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
from pathlib import Path

from sqlalchemy import create_engine, text

DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime",
)


def query_scalar(conn, sql: str, **params) -> int:
    try:
        result = conn.execute(text(sql), params)
        value = result.scalar_one_or_none()
        return int(value or 0)
    except Exception:
        return 0


def collect_metrics(days: int) -> dict[str, int]:
    engine = create_engine(DEFAULT_DB_URL, future=True)
    start_time = dt.datetime.utcnow() - dt.timedelta(days=days)
    metrics: dict[str, int] = {}
    with engine.connect() as conn:
        metrics["import_total"] = query_scalar(conn, "SELECT COUNT(*) FROM import_batches")
        metrics["import_last_days"] = query_scalar(
            conn,
            "SELECT COUNT(*) FROM import_batches WHERE finished_at >= :start",
            start=start_time,
        )
        metrics["chat_sessions"] = query_scalar(conn, "SELECT COUNT(*) FROM query_sessions")
        metrics["export_jobs"] = query_scalar(conn, "SELECT COUNT(*) FROM export_jobs")
        metrics["failed_exports"] = query_scalar(
            conn,
            "SELECT COUNT(*) FROM export_jobs WHERE status='failed'",
        )
    return metrics


def write_csv(metrics: dict[str, int], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, value])
    print(f"指标已写入 {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="导出近期指标")
    parser.add_argument("--days", type=int, default=7, help="统计最近天数，默认为 7 天")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("metrics/report.csv"),
        help="输出 CSV 路径",
    )
    args = parser.parse_args()
    metrics = collect_metrics(args.days)
    write_csv(metrics, args.output)


if __name__ == "__main__":
    main()
