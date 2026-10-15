"""Narrative spec cards. Numeric metrics live on the semantic model."""

from __future__ import annotations

from src.residuedesk.schemas import Commodity
from src.residuedesk.semantic import COMMODITY_METRICS

FIBER = {item.commodity for item in COMMODITY_METRICS.values() if item.fiber}

# Built from the semantic model so the grader and the model cannot drift.
SPECS: dict[Commodity, dict[str, float | str]] = {
    commodity: {
        "accept_max": metrics.accept_max,
        "resort_max": metrics.resort_max,
        "moisture_cap": metrics.moisture_cap,
        "label": metrics.label,
        "card_id": metrics.card_id,
    }
    for commodity, metrics in COMMODITY_METRICS.items()
}

SPEC_CARDS: dict[str, str] = {
    "SPEC-OCC-01": (
        "OCC fiber card. Experimental accept band is residue at or below 5 percent. "
        "Between 5 and 12 percent I send the load to the resort bay. Above 12 percent "
        "it diverts. Moisture above 18 percent worsens the call by one step because "
        "wet corrugated blinds the optical sorters in this PoC."
    ),
    "SPEC-MXP-01": (
        "Mixed paper card. Accept at or below 8 percent residue. Resort through 18. "
        "Moisture cap is 16 percent. I treat mixed paper as more tolerant than OCC "
        "because the sample mill note I wrote allows a wider outthrow band."
    ),
    "SPEC-PET-01": (
        "PET bottle card. Accept at or below 4 percent residue. Resort through 10. "
        "Sleeve labels show up in spot-check notes and do not auto-reject, but they "
        "keep the load in whatever residue band the scale ticket already earned."
    ),
    "SPEC-HDPE-01": (
        "HDPE natural card. Same residue bands as PET in this experiment. A battery, "
        "propane cylinder, or lithium note overrides the grade and quarantines the load."
    ),
    "SPEC-GLS-01": (
        "Glass cullet card. Accept at or below 6 percent residue. Ceramic or stoneware "
        "mentioned in the spot check forces a divert even when residue looks clean, "
        "because ceramics survive the furnace in this simplified model."
    ),
    "SPEC-FILM-01": (
        "LDPE film card. Wider bands: accept through 10 percent, resort through 25. "
        "Film loads above 25 percent residue go to the bunker. I set the wider band "
        "after the first sample run, where clean film still carried loose paper."
    ),
}

PROHIBITED_TERMS = ("battery", "propane", "syringe", "aerosol", "lithium")

LINE_FOR = {
    "accept": "tip_floor_primary",
    "resort": "qc_bay_2",
    "divert": "residue_bunker",
    "reject": "quarantine_pad",
}
