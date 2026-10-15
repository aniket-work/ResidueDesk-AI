"""Specialist agents. Each one appends a trace line and returns a narrow result."""

from __future__ import annotations

from src.residuedesk.rules import FIBER, PROHIBITED_TERMS, SPECS
from src.residuedesk.schemas import Disposition, InboundLoad


def intake_agent(load: InboundLoad, trace: list[str]) -> list[str]:
    flags: list[str] = []
    if load.net_weight_lb < 400:
        flags.append("underweight_ticket")
    if not load.supplier_id.strip():
        flags.append("missing_supplier")
    if not load.received_at.strip():
        flags.append("missing_timestamp")
    trace.append(
        f"intake: {load.load_id} {load.commodity.value} "
        f"{load.net_weight_lb} lb flags={flags or ['ok']}"
    )
    return flags


def residue_scout(load: InboundLoad, trace: list[str]) -> list[str]:
    notes = load.spot_check_notes.lower()
    hits = [term for term in PROHIBITED_TERMS if term in notes]
    trace.append(
        f"scout: residue={load.residue_percent:.1f}% "
        f"moisture={load.moisture_percent:.1f}% prohibited={hits or ['none']}"
    )
    return hits


def commodity_grader(load: InboundLoad, trace: list[str]) -> tuple[str, str, str, bool]:
    spec = SPECS[load.commodity]
    accept_max = float(spec["accept_max"])
    resort_max = float(spec["resort_max"])
    moisture_cap = float(spec["moisture_cap"])
    if load.residue_percent <= accept_max:
        band = "in_grade"
    elif load.residue_percent <= resort_max:
        band = "out_of_grade"
    else:
        band = "heavy_residue"
    moisture_breach = load.commodity in FIBER and load.moisture_percent > moisture_cap
    label = str(spec["label"])
    card_id = str(spec["card_id"])
    trace.append(
        f"grader: card={card_id} band={band} moisture_breach={moisture_breach}"
    )
    return band, label, card_id, moisture_breach


def _worsen(disposition: Disposition) -> Disposition:
    if disposition == Disposition.ACCEPT:
        return Disposition.RESORT
    if disposition == Disposition.RESORT:
        return Disposition.DIVERT
    return disposition


def line_router(
    load: InboundLoad,
    prohibited: list[str],
    band: str,
    moisture_breach: bool,
    intake_flags: list[str],
    trace: list[str],
) -> tuple[Disposition, list[str]]:
    reasons: list[str] = []
    notes = load.spot_check_notes.lower()

    if prohibited:
        reasons.append("prohibited:" + ",".join(prohibited))
        trace.append(f"router: reject quarantine because {reasons[0]}")
        return Disposition.REJECT, reasons

    if "ceramic" in notes or "stoneware" in notes:
        reasons.append("non_spec_ceramic")
        trace.append("router: ceramic note forces divert")
        return Disposition.DIVERT, reasons

    band_map = {
        "in_grade": Disposition.ACCEPT,
        "out_of_grade": Disposition.RESORT,
        "heavy_residue": Disposition.DIVERT,
    }
    disposition = band_map[band]
    reasons.append(band)

    if moisture_breach:
        before = disposition
        disposition = _worsen(disposition)
        reasons.append("moisture_cap")
        trace.append(f"router: moisture worsened {before.value} -> {disposition.value}")

    if "underweight_ticket" in intake_flags and disposition == Disposition.ACCEPT:
        disposition = Disposition.RESORT
        reasons.append("underweight_ticket")

    trace.append(f"router: disposition={disposition.value} reasons={reasons}")
    return disposition, reasons


def shift_briefer(
    load: InboundLoad,
    disposition: Disposition,
    reasons: list[str],
    line_assignment: str,
    trace: list[str],
) -> str:
    reason_text = ", ".join(reasons) if reasons else "no flags"
    line = (
        f"{load.load_id} {disposition.value} -> {line_assignment} "
        f"({load.commodity.value}, residue {load.residue_percent:.1f}%, {reason_text})"
    )
    trace.append(f"briefer: {line}")
    return line
