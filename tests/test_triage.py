"""Checks for the experimental triage rules."""

from __future__ import annotations

import json
from pathlib import Path

from src.residuedesk.coordinator import run_shift
from src.residuedesk.schemas import Commodity, Disposition, InboundLoad

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample_loads.json"


def _load(**overrides) -> InboundLoad:
    base = {
        "load_id": "LD-T",
        "supplier_id": "SUP-1",
        "commodity": Commodity.OCC,
        "net_weight_lb": 10000,
        "residue_percent": 3.0,
        "moisture_percent": 8.0,
        "spot_check_notes": "",
        "received_at": "2026-10-14T06:00:00",
    }
    base.update(overrides)
    return InboundLoad.model_validate(base)


def test_clean_occ_accepts() -> None:
    report = run_shift([_load()], "test")
    assert report.decisions[0].disposition == Disposition.ACCEPT
    assert report.decisions[0].line_assignment == "tip_floor_primary"


def test_battery_note_rejects() -> None:
    report = run_shift(
        [_load(commodity=Commodity.HDPE, spot_check_notes="battery pack in gaylord")],
        "test",
    )
    decision = report.decisions[0]
    assert decision.disposition == Disposition.REJECT
    assert decision.line_assignment == "quarantine_pad"
    assert any(reason.startswith("prohibited:") for reason in decision.reasons)


def test_wet_mixed_paper_worsens_to_resort() -> None:
    report = run_shift(
        [
            _load(
                commodity=Commodity.MIXED_PAPER,
                residue_percent=6.2,
                moisture_percent=19.4,
            )
        ],
        "test",
    )
    decision = report.decisions[0]
    assert decision.grade_band == "in_grade"
    assert decision.disposition == Disposition.RESORT
    assert "moisture_cap" in decision.reasons


def test_ceramic_glass_diverts() -> None:
    report = run_shift(
        [
            _load(
                commodity=Commodity.GLASS,
                residue_percent=4.4,
                spot_check_notes="ceramic mug fragments",
            )
        ],
        "test",
    )
    assert report.decisions[0].disposition == Disposition.DIVERT
    assert "non_spec_ceramic" in report.decisions[0].reasons


def test_underweight_clean_ticket_goes_to_resort() -> None:
    report = run_shift([_load(net_weight_lb=280, residue_percent=2.8)], "test")
    assert report.decisions[0].disposition == Disposition.RESORT
    assert "underweight_ticket" in report.decisions[0].reasons


def test_semantic_projection_binds_measures() -> None:
    from src.residuedesk.semantic import MEASURES, RELATIONSHIPS, project_load

    projected = project_load(_load(residue_percent=3.2, moisture_percent=8.0, net_weight_lb=18420))
    assert {item.name for item in MEASURES} == {
        "NetWeightLb",
        "ResiduePercent",
        "MoisturePercent",
    }
    assert projected.measures["ResiduePercent"] == 3.2
    assert projected.metrics.card_id == "SPEC-OCC-01"
    assert projected.metrics.fiber is True
    assert any(item.name == "LoadCommodity" for item in RELATIONSHIPS)


def test_sample_file_counts() -> None:
    payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
    loads = [InboundLoad.model_validate(item) for item in payload["loads"]]
    report = run_shift(loads, payload["facility_name"])
    assert report.counts == {"accept": 2, "resort": 4, "divert": 3, "reject": 1}
    assert "LD-106" in report.shift_brief
    assert report.decisions[0].agent_trace[0].startswith("intake:")
