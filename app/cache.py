from __future__ import annotations

import hashlib
import json

from app.models import Performance

CACHE_VERSION = "playeriq-analysis-cache-v1"


def _performance_snapshot(row: Performance) -> dict:
    return {
        "id": row.id,
        "match_date": row.match_date.isoformat(),
        "opponent": row.opponent,
        "position": row.position,
        "minutes_played": row.minutes_played,
        "goals": row.goals,
        "assists": row.assists,
        "shots": row.shots,
        "key_passes": row.key_passes,
        "tackles": row.tackles,
        "interceptions": row.interceptions,
        "rating": row.rating,
        "rpe": row.rpe,
        "notes": row.notes,
    }


def build_analysis_cache_key(
    *,
    player_name: str,
    rows: list[Performance],
    window: int,
    model: str,
    prompt_version: str,
) -> str:
    payload = {
        "cache_version": CACHE_VERSION,
        "prompt_version": prompt_version,
        "model": model,
        "player_name": player_name,
        "window": window,
        "performances": [
            _performance_snapshot(row)
            for row in rows
        ],
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
