from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DARK = colors.HexColor("#111827")
MUTED = colors.HexColor("#6B7280")
LIGHT = colors.HexColor("#F3F4F6")
BORDER = colors.HexColor("#D1D5DB")


def _safe(value: object) -> str:
    return escape(str(value if value is not None else ""))


def _metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def build_performance_report(
    *,
    player_name: str,
    metrics: dict,
    analysis: dict,
    window: int,
) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=17 * mm,
        title=f"PlayerIQ Performance Report - {player_name}",
        author="PlayerIQ",
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "PlayerIQTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=DARK,
        alignment=TA_LEFT,
        spaceAfter=3 * mm,
    )
    subtitle = ParagraphStyle(
        "PlayerIQSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=MUTED,
        spaceAfter=5 * mm,
    )
    heading = ParagraphStyle(
        "PlayerIQHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=DARK,
        spaceBefore=4 * mm,
        spaceAfter=2 * mm,
    )
    body = ParagraphStyle(
        "PlayerIQBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=DARK,
    )
    small = ParagraphStyle(
        "PlayerIQSmall",
        parent=body,
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    )
    insight_title = ParagraphStyle(
        "PlayerIQInsightTitle",
        parent=body,
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=DARK,
        spaceAfter=1 * mm,
    )

    story = [
        Paragraph("PlayerIQ", title),
        Paragraph(
            (
                "Performance Intelligence Report | "
                f"{_safe(player_name)} | Latest {window} matches"
            ),
            subtitle,
        ),
    ]

    current = metrics["current"]
    previous = metrics.get("previous")

    cards = [
        [
            "Avg rating",
            _metric(current["average_rating"]),
            "Minutes",
            _metric(current["minutes"]),
        ],
        [
            "Goal contrib. / 90",
            _metric(current["goal_contributions_per_90"]),
            "Key passes / 90",
            _metric(current["key_passes_per_90"]),
        ],
    ]

    card_table = Table(
        cards,
        colWidths=[42 * mm, 28 * mm, 42 * mm, 28 * mm],
        hAlign="LEFT",
    )
    card_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(card_table)

    story.append(Paragraph("Verified performance snapshot", heading))

    metric_rows = [
        [
            "Metric",
            f"Latest {window}",
            f"Previous {window}" if previous else "Previous",
        ],
        [
            "Average rating",
            _metric(current["average_rating"]),
            _metric(previous["average_rating"]) if previous else "N/A",
        ],
        [
            "Goals / 90",
            _metric(current["goals_per_90"]),
            _metric(previous["goals_per_90"]) if previous else "N/A",
        ],
        [
            "Assists / 90",
            _metric(current["assists_per_90"]),
            _metric(previous["assists_per_90"]) if previous else "N/A",
        ],
        [
            "Goal contributions / 90",
            _metric(current["goal_contributions_per_90"]),
            (
                _metric(previous["goal_contributions_per_90"])
                if previous
                else "N/A"
            ),
        ],
        [
            "Key passes / 90",
            _metric(current["key_passes_per_90"]),
            _metric(previous["key_passes_per_90"]) if previous else "N/A",
        ],
        [
            "Tackles / 90",
            _metric(current["tackles_per_90"]),
            _metric(previous["tackles_per_90"]) if previous else "N/A",
        ],
        [
            "Interceptions / 90",
            _metric(current["interceptions_per_90"]),
            (
                _metric(previous["interceptions_per_90"])
                if previous
                else "N/A"
            ),
        ],
        [
            "Average RPE",
            _metric(current["average_rpe"]),
            _metric(previous["average_rpe"]) if previous else "N/A",
        ],
    ]

    metric_table = Table(
        metric_rows,
        colWidths=[78 * mm, 44 * mm, 44 * mm],
        repeatRows=1,
        hAlign="LEFT",
    )
    metric_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, LIGHT],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(metric_table)

    story.append(Paragraph("AI performance interpretation", heading))
    story.append(Paragraph(_safe(analysis["summary"]), body))

    def add_insights(
        section_title: str,
        items: list[dict],
    ) -> None:
        story.append(Paragraph(section_title, heading))
        for index, item in enumerate(items, start=1):
            story.append(
                KeepTogether(
                    [
                        Paragraph(
                            f"{index}. {_safe(item['title'])}",
                            insight_title,
                        ),
                        Paragraph(
                            f"<b>Evidence:</b> {_safe(item['evidence'])}",
                            body,
                        ),
                        Paragraph(
                            _safe(item["interpretation"]),
                            body,
                        ),
                        Spacer(1, 2.2 * mm),
                    ]
                )
            )

    add_insights(
        "Evidence-backed strengths",
        analysis["strengths"],
    )
    add_insights(
        "Development areas",
        analysis["development_areas"],
    )

    story.append(Paragraph("Training priorities", heading))
    for index, item in enumerate(
        analysis["training_priorities"],
        start=1,
    ):
        story.append(
            KeepTogether(
                [
                    Paragraph(
                        f"{index}. {_safe(item['priority'])}",
                        insight_title,
                    ),
                    Paragraph(
                        _safe(item["reason"]),
                        body,
                    ),
                    Spacer(1, 2.2 * mm),
                ]
            )
        )

    story.append(Paragraph("Data and confidence notes", heading))
    story.append(
        Paragraph(
            _safe(analysis["confidence_note"]),
            body,
        )
    )
    story.append(Spacer(1, 2 * mm))
    story.append(
        Paragraph(
            (
                "PlayerIQ calculates statistics deterministically from the "
                "player's stored performance entries before AI "
                "interpretation. The report reflects self-entered "
                "performance data and should not be presented as official "
                "tracking or scouting data."
            ),
            small,
        )
    )

    def footer(canvas, current_doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.4)
        canvas.line(
            current_doc.leftMargin,
            11 * mm,
            A4[0] - current_doc.rightMargin,
            11 * mm,
        )
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            current_doc.leftMargin,
            7 * mm,
            "PlayerIQ | Evidence before judgment",
        )
        canvas.drawRightString(
            A4[0] - current_doc.rightMargin,
            7 * mm,
            f"Page {current_doc.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )

    return buffer.getvalue()
