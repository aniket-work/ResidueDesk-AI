"""Pydantic contracts for inbound loads and shift decisions."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Commodity(str, Enum):
    OCC = "occ"
    MIXED_PAPER = "mixed_paper"
    PET = "pet"
    HDPE = "hdpe"
    GLASS = "glass"
    LDPE_FILM = "ldpe_film"


class Disposition(str, Enum):
    ACCEPT = "accept"
    RESORT = "resort"
    DIVERT = "divert"
    REJECT = "reject"


class InboundLoad(BaseModel):
    load_id: str
    supplier_id: str
    commodity: Commodity
    net_weight_lb: int = Field(ge=0, le=80_000)
    residue_percent: float = Field(ge=0.0, le=100.0)
    moisture_percent: float = Field(ge=0.0, le=100.0)
    spot_check_notes: str = ""
    received_at: str


class LoadDecision(BaseModel):
    load_id: str
    supplier_id: str
    commodity: Commodity
    net_weight_lb: int
    residue_percent: float
    moisture_percent: float
    disposition: Disposition
    grade_band: str
    grade_label: str
    line_assignment: str
    reasons: list[str]
    brief_line: str
    agent_trace: list[str]
    spec_card_id: str


class ShiftReport(BaseModel):
    facility_name: str
    decisions: list[LoadDecision]
    shift_brief: str
    counts: dict[str, int]
    avg_residue_percent: float
