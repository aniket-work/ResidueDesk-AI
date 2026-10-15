"""FastAPI surface over the same coordinator the CLI uses."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from src.residuedesk.coordinator import run_shift
from src.residuedesk.schemas import InboundLoad, ShiftReport

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PATH = ROOT / "sample_loads.json"
DASHBOARD_PATH = ROOT / "static" / "dashboard.html"

app = FastAPI(title="ResidueDesk-AI", version="0.1.0")


def load_sample() -> list[InboundLoad]:
    payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return [InboundLoad.model_validate(item) for item in payload["loads"]]


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_PATH.read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "facility": "north-wharf-mrf-poc"}


@app.post("/api/triage/sample", response_model=ShiftReport)
def triage_sample() -> ShiftReport:
    return run_shift(load_sample(), "North Wharf MRF PoC")


@app.post("/api/triage", response_model=ShiftReport)
def triage_custom(loads: list[InboundLoad]) -> ShiftReport:
    return run_shift(loads, "North Wharf MRF PoC")
