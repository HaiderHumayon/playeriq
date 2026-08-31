from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.models import Performance


def _round(value: float) -> float:
    return round(value, 2)


def _per90(total: int, minutes: int) -> float:
    if minutes <= 0:
        return 0.0
    return _round((total / minutes) * 90)


def calculate_metrics(rows: list[Performance]) -> dict:
    matches = len(rows)
    minutes = sum(row.minutes_played for row in rows)
    goals = sum(row.goals for row in rows)
    assists = sum(row.assists for row in rows)
    shots = sum(row.shots for row in rows)
    key_passes = sum(row.key_passes for row in rows)
    tackles = sum(row.tackles for row in rows)
    interceptions = sum(row.interceptions for row in rows)

    if matches:
        average_rating = _round(sum(row.rating for row in rows) / matches)
        average_rpe = _round(sum(row.rpe for row in rows) / matches)
    else:
        average_rating = 0.0
        average_rpe = 0.0

    return {
        "matches": matches,
        "minutes": minutes,
        "goals": goals,
        "assists": assists,
        "goal_contributions": goals + assists,
        "shots": shots,
        "key_passes": key_passes,
        "tackles": tackles,
        "interceptions": interceptions,
        "average_rating": average_rating,
        "average_rpe": average_rpe,
        "goals_per_90": _per90(goals, minutes),
        "assists_per_90": _per90(assists, minutes),
        "goal_contributions_per_90": _per90(goals + assists, minutes),
        "shots_per_90": _per90(shots, minutes),
        "key_passes_per_90": _per90(key_passes, minutes),
        "tackles_per_90": _per90(tackles, minutes),
        "interceptions_per_90": _per90(interceptions, minutes),
    }


def _trend(current: float, previous: float, tolerance: float = 0.01) -> dict:
    change = _round(current - previous)

    direction: Literal["up", "down", "flat"]
    if change > tolerance:
        direction = "up"
    elif change < -tolerance:
        direction = "down"
    else:
        direction = "flat"

    return {
        "current": current,
        "previous": previous,
        "change": change,
        "direction": direction,
    }


def build_summary(
    rows_descending: list[Performance],
    window: int,
) -> dict:
    current_rows = rows_descending[:window]
    previous_rows = rows_descending[window : window * 2]

    current = calculate_metrics(current_rows)
    previous = calculate_metrics(previous_rows) if previous_rows else None

    trends = None
    if previous_rows:
        trends = {
            "average_rating": _trend(
                current["average_rating"],
                previous["average_rating"],
            ),
            "goal_contributions_per_90": _trend(
                current["goal_contributions_per_90"],
                previous["goal_contributions_per_90"],
            ),
            "key_passes_per_90": _trend(
                current["key_passes_per_90"],
                previous["key_passes_per_90"],
            ),
            "tackles_per_90": _trend(
                current["tackles_per_90"],
                previous["tackles_per_90"],
            ),
        }

    return {
        "window_size": window,
        "current": current,
        "previous": previous,
        "trends": trends,
        "evidence_note": (
            "All metrics are calculated deterministically from stored "
            "performance records. No AI is used to calculate these numbers."
        ),
    }
