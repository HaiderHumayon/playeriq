# My 10x Solution - Haider Humayon

## PlayerIQ - AI Football Performance Intelligence

**Repository:** https://github.com/HaiderHumayon/playeriq

## Problem

Football performance is often reviewed too subjectively. Players are described as "good", "bad", "in form", or "not contributing enough" without enough structured evidence behind those judgments. Individual match statistics and trends are often spread across notes, spreadsheets, or memory, which makes consistent self-review difficult.

## My 10x solution

PlayerIQ turns performance review into a repeatable evidence workflow:

**Record -> Measure -> Compare -> Understand -> Improve**

The 10x claim is a product target: PlayerIQ can turn a manual 20-30 minute review process into a data-backed analysis and downloadable report in under two minutes for a prepared player dataset. The system is not intended to replace professional scouting or official tracking data.

## Implementation in plain language

A player creates an account and logs in. JWT authentication protects private routes and every performance is attached to the authenticated user.

The player records match performances through a FastAPI endpoint. Pydantic validates the inputs and PostgreSQL stores them so the records survive service restarts.

Python calculates the football statistics before AI is involved. These include average rating, average RPE, minutes, goals and assists per 90, goal contributions per 90, shots, key passes, tackles and interceptions per 90, plus comparisons between the latest and previous performance windows.

The AI Performance Analyst receives those verified statistics and performs one narrow task: interpret the evidence. It returns a structured summary, evidence-backed strengths, development areas, training priorities, and a confidence note. The response is validated with Pydantic before it can be saved or returned.

PlayerIQ also creates a SHA-256 cache key from the player, performance records, analysis window, model, and prompt version. If the inputs have not changed, the saved PostgreSQL analysis is returned instead of making another LLM call.

Finally, a PDF endpoint produces a professional PlayerIQ performance report from the verified statistics and cached AI analysis.

## Program concepts implemented

| Concept | Implementation | Code location |
|---|---|---|
| API endpoints | FastAPI HTTP API with validation and status codes | `app/main.py` |
| Database | PostgreSQL persistence via SQLAlchemy | `app/database.py`, `app/models.py` |
| Authentication | JWT login and user-level data isolation | `app/auth.py` |
| LLM integration | Narrow, validated performance interpretation | `app/llm.py` |
| Caching | Persistent SHA-256 analysis cache | `app/cache.py`, `ai_analyses` |
| PDF reporting | Downloadable evidence-based report | `app/reports.py` |

**Swaps:** None. PlayerIQ uses six concepts from the main capstone list.

## Scope

**Explicit non-goal:** PlayerIQ does not perform automated video analysis or computer-vision tracking.

GPS integration, team management, a scouting marketplace, a mobile app, and automated medical assessment are also outside the capstone core.

## Run steps

1. Copy `.env.example` to `.env`, choose a local database password and 32+ character JWT secret, and add a Groq API key.
2. Run `docker compose up -d --build`.
3. Run `docker compose exec api python -m scripts.seed_demo`.
4. Open `http://localhost:8010/docs` and follow the README 5-minute demo path.

## Data and AI boundaries

The statistics are calculated deterministically in Python before the LLM is called. AI is used for interpretation, not primary metric calculation. Demo data is synthetic, and user-entered statistics are treated as self-reported rather than official event-tracking or scouting data. Secrets are loaded from environment variables and are not committed to Git.
