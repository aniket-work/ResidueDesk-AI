#!/usr/bin/env python3
"""CLI for the ResidueDesk-AI shift desk."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.residuedesk.analytics import write_disposition_chart
from src.residuedesk.coordinator import run_shift
from src.residuedesk.schemas import InboundLoad

ROOT = Path(__file__).resolve().parent
SAMPLE_PATH = ROOT / "sample_loads.json"
console = Console()


def load_tickets(path: Path) -> tuple[str, list[InboundLoad]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    loads = [InboundLoad.model_validate(item) for item in payload["loads"]]
    return str(payload.get("facility_name", "ResidueDesk PoC")), loads


def render_table(report) -> None:
    table = Table(title="ResidueDesk-AI — Inbound Contamination Triage")
    table.add_column("Load")
    table.add_column("Commodity")
    table.add_column("Residue %", justify="right")
    table.add_column("Disposition")
    table.add_column("Line")
    for decision in report.decisions:
        table.add_row(
            decision.load_id,
            decision.commodity.value,
            f"{decision.residue_percent:.1f}",
            decision.disposition.value,
            decision.line_assignment,
        )
    console.print(table)
    console.print(report.shift_brief)
    console.print(
        f"[SUCCESS] {len(report.decisions)} loads triaged — "
        f"avg residue {report.avg_residue_percent}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local contamination shift brief.")
    parser.add_argument("--input", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--chart", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    facility, loads = load_tickets(args.input)
    console.print("=" * 60)
    console.print("   ResidueDesk-AI — Recycling Contamination Shift Desk")
    console.print("=" * 60)
    console.print(f"[*] Loading {len(loads)} inbound tickets from {args.input.name}...")
    console.print("[*] Intake -> Scout -> Grader -> Router -> Briefer")
    report = run_shift(loads, facility)
    render_table(report)

    if args.chart:
        written = write_disposition_chart(report, args.chart)
        console.print(f"[*] Chart written to {written}")
    if args.json_out:
        args.json_out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[*] JSON written to {args.json_out}")


if __name__ == "__main__":
    main()
