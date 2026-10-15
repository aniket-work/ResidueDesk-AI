"""Batch charts for the shift summary."""

from __future__ import annotations

from pathlib import Path

from src.residuedesk.schemas import ShiftReport

COLORS = {
    "accept": "#2f9e6b",
    "resort": "#e0a100",
    "divert": "#e07a3d",
    "reject": "#d64545",
}


def write_disposition_chart(report: ShiftReport, path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = ["accept", "resort", "divert", "reject"]
    values = [report.counts.get(label, 0) for label in labels]
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8.2, 3.2), dpi=120)
    fig.patch.set_facecolor("#0f1622")
    ax.set_facecolor("#0f1622")
    bars = ax.bar(labels, values, color=[COLORS[label] for label in labels], width=0.62)
    ax.set_title(
        f"{report.facility_name} — disposition counts (avg residue {report.avg_residue_percent}%)",
        color="#e3edf7",
        fontsize=11,
        pad=10,
    )
    ax.tick_params(colors="#c5d4e6")
    ax.spines["bottom"].set_color("#304a6e")
    ax.spines["left"].set_color("#304a6e")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel("loads", color="#c5d4e6")
    ax.set_ylim(0, max(values + [1]) + 1)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.08,
            str(value),
            ha="center",
            color="#e3edf7",
            fontsize=10,
        )
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path
