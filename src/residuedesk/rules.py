"""Experimental commodity specs I chose for this PoC. Not a mill contract."""

from __future__ import annotations

from src.residuedesk.schemas import Commodity

FIBER = {Commodity.OCC, Commodity.MIXED_PAPER}

# accept_max: residue at or below this can land on the primary tip line.
# resort_max: residue above accept and at or below this goes to the QC bay.
# anything above resort_max is heavy residue and diverts to the bunker.
SPECS: dict[Commodity, dict[str, float | str]] = {
    Commodity.OCC: {
        "accept_max": 5.0,
        "resort_max": 12.0,
        "moisture_cap": 18.0,
        "label": "OCC fiber",
        "card_id": "SPEC-OCC-01",
    },
    Commodity.MIXED_PAPER: {
        "accept_max": 8.0,
        "resort_max": 18.0,
        "moisture_cap": 16.0,
        "label": "Mixed paper",
        "card_id": "SPEC-MXP-01",
    },
    Commodity.PET: {
        "accept_max": 4.0,
        "resort_max": 10.0,
        "moisture_cap": 8.0,
        "label": "PET bottles",
        "card_id": "SPEC-PET-01",
    },
    Commodity.HDPE: {
        "accept_max": 4.0,
        "resort_max": 10.0,
        "moisture_cap": 8.0,
        "label": "HDPE natural",
        "card_id": "SPEC-HDPE-01",
    },
    Commodity.GLASS: {
        "accept_max": 6.0,
        "resort_max": 15.0,
        "moisture_cap": 12.0,
        "label": "Glass cullet",
        "card_id": "SPEC-GLS-01",
    },
    Commodity.LDPE_FILM: {
        "accept_max": 10.0,
        "resort_max": 25.0,
        "moisture_cap": 12.0,
        "label": "LDPE film",
        "card_id": "SPEC-FILM-01",
    },
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
