"""Coordinator that runs the five specialists and writes the shift brief."""

from __future__ import annotations

from src.residuedesk.agents import (
    commodity_grader,
    intake_agent,
    line_router,
    residue_scout,
    shift_briefer,
)
from src.residuedesk.rules import LINE_FOR, SPEC_CARDS
from src.residuedesk.schemas import Disposition, InboundLoad, LoadDecision, ShiftReport
from src.residuedesk.semantic import project_load

SEVERITY = {
    Disposition.REJECT: 0,
    Disposition.DIVERT: 1,
    Disposition.RESORT: 2,
    Disposition.ACCEPT: 3,
}


def decide_load(load: InboundLoad) -> LoadDecision:
    trace: list[str] = []
    flags = intake_agent(load, trace)
    projected = project_load(load)
    trace.append(
        "semantic: entity=Load "
        f"measures={','.join(projected.measures)} "
        f"commodity={projected.commodity.value} "
        f"card={projected.metrics.card_id}"
    )
    prohibited = residue_scout(load, trace)
    band, label, card_id, moisture_breach = commodity_grader(load, trace)
    disposition, reasons = line_router(
        load, prohibited, band, moisture_breach, flags, trace
    )
    line_assignment = LINE_FOR[disposition.value]
    brief_line = shift_briefer(load, disposition, reasons, line_assignment, trace)
    card_text = SPEC_CARDS[card_id]
    trace.append(f"card: {card_text[:72]}...")
    return LoadDecision(
        load_id=load.load_id,
        supplier_id=load.supplier_id,
        commodity=load.commodity,
        net_weight_lb=load.net_weight_lb,
        residue_percent=load.residue_percent,
        moisture_percent=load.moisture_percent,
        disposition=disposition,
        grade_band=band,
        grade_label=label,
        line_assignment=line_assignment,
        reasons=reasons,
        brief_line=brief_line,
        agent_trace=trace,
        spec_card_id=card_id,
    )


def _counts(decisions: list[LoadDecision]) -> dict[str, int]:
    counts = {item.value: 0 for item in Disposition}
    for decision in decisions:
        counts[decision.disposition.value] += 1
    return counts


def _brief(facility_name: str, decisions: list[LoadDecision], counts: dict[str, int]) -> str:
    ordered = sorted(decisions, key=lambda item: (SEVERITY[item.disposition], item.load_id))
    lines = [
        f"SHIFT BRIEF — {facility_name}",
        (
            f"Loads {len(decisions)} | accept {counts['accept']} | "
            f"resort {counts['resort']} | divert {counts['divert']} | "
            f"reject {counts['reject']}"
        ),
        "Priority queue (reject and divert first):",
    ]
    for index, decision in enumerate(ordered, start=1):
        lines.append(f"{index}. {decision.brief_line}")
    return "\n".join(lines)


def run_shift(loads: list[InboundLoad], facility_name: str) -> ShiftReport:
    decisions = [decide_load(load) for load in loads]
    counts = _counts(decisions)
    residue_values = [item.residue_percent for item in decisions]
    avg_residue = sum(residue_values) / len(residue_values) if residue_values else 0.0
    return ShiftReport(
        facility_name=facility_name,
        decisions=decisions,
        shift_brief=_brief(facility_name, decisions, counts),
        counts=counts,
        avg_residue_percent=round(avg_residue, 2),
    )
