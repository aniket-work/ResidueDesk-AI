"""Semantic model the shift desk reads. Agents do not own these definitions."""

from __future__ import annotations

from pydantic import BaseModel

from src.residuedesk.schemas import Commodity, InboundLoad


class Entity(BaseModel):
    name: str
    grain: str
    key: str
    description: str


class Measure(BaseModel):
    name: str
    entity: str
    unit: str
    definition: str


class Relationship(BaseModel):
    name: str
    from_entity: str
    to_entity: str
    cardinality: str


class CommodityMetrics(BaseModel):
    commodity: Commodity
    label: str
    card_id: str
    accept_max: float
    resort_max: float
    moisture_cap: float
    fiber: bool


class LoadProjection(BaseModel):
    """One ticket lifted onto the semantic layer."""

    load_id: str
    supplier_id: str
    commodity: Commodity
    measures: dict[str, float]
    note: str
    received_at: str
    metrics: CommodityMetrics
    entity: str = "Load"


ENTITIES: tuple[Entity, ...] = (
    Entity(
        name="Load",
        grain="one inbound ticket",
        key="load_id",
        description="The fact table. One row is one scale-house ticket.",
    ),
    Entity(
        name="Commodity",
        grain="material class",
        key="commodity",
        description="OCC, mixed paper, PET, HDPE, glass, or LDPE film.",
    ),
    Entity(
        name="Supplier",
        grain="supplier code on the ticket",
        key="supplier_id",
        description="Who delivered the load. Stored, not scored, in this PoC.",
    ),
)

MEASURES: tuple[Measure, ...] = (
    Measure(
        name="NetWeightLb",
        entity="Load",
        unit="lb",
        definition="Net pounds on the scale ticket. Under 400 lb is an underweight flag.",
    ),
    Measure(
        name="ResiduePercent",
        entity="Load",
        unit="percent",
        definition="Spot-check residue. The commodity metrics band this measure.",
    ),
    Measure(
        name="MoisturePercent",
        entity="Load",
        unit="percent",
        definition="Moisture on the ticket. Compared with moisture_cap only for fiber commodities.",
    ),
)

RELATIONSHIPS: tuple[Relationship, ...] = (
    Relationship(
        name="LoadCommodity",
        from_entity="Load",
        to_entity="Commodity",
        cardinality="many_to_one",
    ),
    Relationship(
        name="LoadSupplier",
        from_entity="Load",
        to_entity="Supplier",
        cardinality="many_to_one",
    ),
)

COMMODITY_METRICS: dict[Commodity, CommodityMetrics] = {
    Commodity.OCC: CommodityMetrics(
        commodity=Commodity.OCC,
        label="OCC fiber",
        card_id="SPEC-OCC-01",
        accept_max=5.0,
        resort_max=12.0,
        moisture_cap=18.0,
        fiber=True,
    ),
    Commodity.MIXED_PAPER: CommodityMetrics(
        commodity=Commodity.MIXED_PAPER,
        label="Mixed paper",
        card_id="SPEC-MXP-01",
        accept_max=8.0,
        resort_max=18.0,
        moisture_cap=16.0,
        fiber=True,
    ),
    Commodity.PET: CommodityMetrics(
        commodity=Commodity.PET,
        label="PET bottles",
        card_id="SPEC-PET-01",
        accept_max=4.0,
        resort_max=10.0,
        moisture_cap=8.0,
        fiber=False,
    ),
    Commodity.HDPE: CommodityMetrics(
        commodity=Commodity.HDPE,
        label="HDPE natural",
        card_id="SPEC-HDPE-01",
        accept_max=4.0,
        resort_max=10.0,
        moisture_cap=8.0,
        fiber=False,
    ),
    Commodity.GLASS: CommodityMetrics(
        commodity=Commodity.GLASS,
        label="Glass cullet",
        card_id="SPEC-GLS-01",
        accept_max=6.0,
        resort_max=15.0,
        moisture_cap=12.0,
        fiber=False,
    ),
    Commodity.LDPE_FILM: CommodityMetrics(
        commodity=Commodity.LDPE_FILM,
        label="LDPE film",
        card_id="SPEC-FILM-01",
        accept_max=10.0,
        resort_max=25.0,
        moisture_cap=12.0,
        fiber=False,
    ),
}

UNDERWEIGHT_LB = 400.0


def project_load(load: InboundLoad) -> LoadProjection:
    """Lift a raw ticket onto Load, with measures and the commodity metric row."""
    metrics = COMMODITY_METRICS[load.commodity]
    return LoadProjection(
        load_id=load.load_id,
        supplier_id=load.supplier_id,
        commodity=load.commodity,
        measures={
            "NetWeightLb": float(load.net_weight_lb),
            "ResiduePercent": float(load.residue_percent),
            "MoisturePercent": float(load.moisture_percent),
        },
        note=load.spot_check_notes,
        received_at=load.received_at,
        metrics=metrics,
    )


def measure_names() -> list[str]:
    return [item.name for item in MEASURES]
