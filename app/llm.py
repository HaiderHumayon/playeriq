from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from pydantic import ValidationError

from app.schemas import PerformanceAnalysis

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"
PROMPT_VERSION = "playeriq-performance-analyst-v1"

# Current public list pricing for openai/gpt-oss-120b on Groq:
# input $0.15 / 1M tokens; output $0.60 / 1M tokens.
# This is an estimated provider-equivalent cost. A free-tier user's actual
# billed amount may remain $0.
INPUT_USD_PER_MILLION = 0.15
OUTPUT_USD_PER_MILLION = 0.60


class LLMError(RuntimeError):
    pass


@dataclass
class Usage:
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_provider_cost_usd: float


def model_name() -> str:
    return os.getenv("GROQ_MODEL", DEFAULT_MODEL)


def _api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        raise LLMError("GROQ_API_KEY is not configured")
    return key


def _schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {
                "type": "string",
            },
            "strengths": {
                "type": "array",
                "minItems": 2,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "evidence": {"type": "string"},
                        "interpretation": {"type": "string"},
                    },
                    "required": ["title", "evidence", "interpretation"],
                },
            },
            "development_areas": {
                "type": "array",
                "minItems": 2,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "evidence": {"type": "string"},
                        "interpretation": {"type": "string"},
                    },
                    "required": ["title", "evidence", "interpretation"],
                },
            },
            "training_priorities": {
                "type": "array",
                "minItems": 2,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "priority": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["priority", "reason"],
                },
            },
            "confidence_note": {
                "type": "string",
            },
        },
        "required": [
            "summary",
            "strengths",
            "development_areas",
            "training_priorities",
            "confidence_note",
        ],
    }


def _estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    cost = (
        (prompt_tokens / 1_000_000) * INPUT_USD_PER_MILLION
        + (completion_tokens / 1_000_000) * OUTPUT_USD_PER_MILLION
    )
    return round(cost, 8)


def analyze_performance(
    *,
    player_name: str,
    metrics: dict,
) -> tuple[PerformanceAnalysis, Usage]:
    model = model_name()

    system = (
        "You are PlayerIQ's football performance analyst. "
        "Your job is narrow: interpret only the verified statistics supplied "
        "by the backend. Never invent match events, context, injuries, "
        "fitness conditions, diagnoses, scouting claims, or metrics that are "
        "not present. Do not label the player simply good or bad. "
        "Every strength and development area must cite numerical evidence "
        "from the supplied metrics. Treat a rising metric as context, not "
        "automatic proof that the player is better overall. "
        "Training priorities must be football-development suggestions, not "
        "medical advice. If the data is insufficient, say so explicitly."
    )

    user = {
        "player_name": player_name,
        "verified_metrics": metrics,
        "task": (
            "Produce a concise evidence-backed performance analysis. "
            "Prioritize measurable trends and explain what the numbers do "
            "and do not support."
        ),
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(user, ensure_ascii=False),
            },
        ],
        "reasoning_effort": "low",
        "max_completion_tokens": 1200,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "playeriq_performance_analysis",
                "strict": True,
                "schema": _schema(),
            },
        },
    }

    request = urllib.request.Request(
        f"{GROQ_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            "User-Agent": "PlayerIQ-Capstone/0.5",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(
            f"Groq API returned HTTP {exc.code}: {detail[:500]}"
        ) from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"Could not reach Groq API: {exc.reason}") from exc

    try:
        envelope = json.loads(raw)
        content = envelope["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        analysis = PerformanceAnalysis.model_validate(parsed)
    except (KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
        raise LLMError(
            "LLM response failed PlayerIQ structured-output validation"
        ) from exc

    usage_data = envelope.get("usage") or {}
    prompt_tokens = int(usage_data.get("prompt_tokens") or 0)
    completion_tokens = int(usage_data.get("completion_tokens") or 0)
    total_tokens = int(
        usage_data.get("total_tokens")
        or (prompt_tokens + completion_tokens)
    )

    usage = Usage(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        estimated_provider_cost_usd=_estimate_cost(
            prompt_tokens,
            completion_tokens,
        ),
    )

    return analysis, usage
