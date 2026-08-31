# PlayerIQ

**AI football performance intelligence built around evidence, not vague labels.**

PlayerIQ is a backend capstone for individual footballers who want to record match performances, calculate meaningful statistics, compare form windows, receive grounded AI interpretation, and generate a professional PDF report.

The project follows a Moneyball-style principle: **use measurable evidence before broad judgments.**

> **Record -> Measure -> Compare -> Understand -> Improve**

## Problem

Football performance is often reviewed too subjectively. Players are described as "good", "bad", "in form", or "not contributing enough" without enough structured evidence behind those judgments. Individual statistics and trends are often spread across notes, spreadsheets, or memory.

PlayerIQ turns those records into a repeatable evidence workflow.

## 10x claim

**Target:** turn a manual 20-30 minute performance review into a data-backed analysis and downloadable report in under two minutes for a prepared player dataset.

This is a product target, not a claim that PlayerIQ replaces professional scouting, official event data, video analysis, or medical judgment.

## Core product

1. Player account with protected personal data.
2. Match performance logging.
3. Performance history, KPIs, and form trends.
4. AI Performance Analyst grounded in verified statistics.
5. Downloadable Player Performance Report.

## Capstone concepts

PlayerIQ implements **six concepts from the main capstone list and uses zero swaps**.

| Concept | Implementation | Code location |
|---|---|---|
| API endpoints | FastAPI HTTP API with validation and correct status codes | `app/main.py` |
| Database | PostgreSQL persistence through SQLAlchemy | `app/database.py`, `app/models.py` |
| Authentication | JWT login plus user-level data isolation | `app/auth.py` |
| LLM integration | Narrow, structured football performance analysis | `app/llm.py` |
| Caching | SHA-256 PostgreSQL-backed AI analysis cache | `app/cache.py`, `ai_analyses` |
| PDF reporting | Downloadable evidence-based report | `app/reports.py`, `/reports/performance.pdf` |

**Swaps: none.**

## Architecture

```text
Player / Swagger
       |
     FastAPI
       |
  +----+-------------+----------------+
  |                  |                |
JWT Auth          PostgreSQL       KPI Engine
                      |                |
               Performances       Verified stats
                      |                |
                      +-------+--------+
                              |
                     AI Performance Analyst
                              |
                     Persistent AI cache
                              |
                      PDF report generator
```

## Evidence-first design

PlayerIQ does **not** ask the LLM to calculate primary football metrics.

Python first calculates:

- average match rating
- average RPE
- goals per 90
- assists per 90
- goal contributions per 90
- shots per 90
- key passes per 90
- tackles per 90
- interceptions per 90
- latest-window versus previous-window changes

The LLM receives those verified values and performs one narrow job: **interpret the evidence**.

The model response is constrained to structured JSON and validated with Pydantic before it is saved or returned.

## Persistent AI caching

Before calling the LLM, PlayerIQ creates a SHA-256 key from the actual analysis inputs:

- authenticated player
- requested analysis window
- performance records
- model
- prompt version

If those inputs have not changed, PlayerIQ returns the saved PostgreSQL analysis with:

```json
{
  "cached": true,
  "provider_call_made": false
}
```

A cache hit creates no additional LLM usage row. New performance data, a different model, prompt version, or analysis window produces a new key.

## PDF reporting

`GET /reports/performance.pdf?window=5` generates a professional PDF from:

- verified current-window statistics
- previous-window comparison
- validated AI summary
- evidence-backed strengths
- development areas
- training priorities
- data/confidence limitations

A current cached analysis must exist first. This prevents a report download from silently triggering an unexpected LLM call.

## Quick start

### Prerequisites

- Docker Desktop
- a Groq API key with available quota

### 1. Configure environment

Copy `.env.example` to `.env`.

Set:

```env
POSTGRES_USER=playeriq
POSTGRES_PASSWORD=choose_a_local_password
POSTGRES_DB=playeriq
JWT_SECRET=choose_a_random_value_at_least_32_characters
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

`.env` is ignored by Git.

### 2. Start PlayerIQ and seed the demo

After the one-time `.env` setup, the app and demo data start with **two commands**:

```powershell
docker compose up -d --build
docker compose exec api python -m scripts.seed_demo
```

Open Swagger:

```text
http://localhost:8010/docs
```

Health check:

```text
http://localhost:8010/health
```

## 5-minute demo path

The seed script creates only synthetic demo data.

**Demo account**

```text
Email: demo@playeriq.local
Password: PlayerIQDemo9!
```

In Swagger:

1. Click **Authorize** and log in with the demo account.
2. Run `GET /performances` - confirm 10 stored match records.
3. Run `GET /analytics/summary?window=5`.
   - current average rating: `7.8`
   - previous average rating: `6.8`
   - current goal contributions / 90: `0.8`
   - current key passes / 90: `3.0`
   - previous key passes / 90: `1.0`
4. Run `POST /analysis/performance?window=5`.
   - the first request should show `cached: false`
   - the AI response contains structured evidence-backed interpretation
5. Run the same analysis again.
   - it should show `cached: true`
   - `provider_call_made: false`
6. Run `GET /analysis/usage`.
   - the cache hit should not create an additional provider-usage row
7. Run `GET /reports/performance.pdf?window=5`.
   - download/open the PlayerIQ PDF report

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/auth/register` | Create player account |
| POST | `/auth/login` | Receive JWT token |
| GET | `/auth/me` | Authenticated profile |
| POST | `/performances` | Store owned match performance |
| GET | `/performances` | List current player's performances |
| GET | `/analytics/summary` | Deterministic KPI and trend summary |
| POST | `/analysis/performance` | Validated AI interpretation |
| GET | `/analysis/usage` | Token and estimated-cost log |
| GET | `/reports/performance.pdf` | Download performance report |

## Security and data boundaries

- passwords are salted and hashed before storage
- protected routes derive identity from the JWT, not request-supplied player names
- performance queries are filtered by authenticated user ID
- secrets live in environment variables and `.env` is ignored
- the Groq API key is never returned by an endpoint or written to application logs
- demo data is synthetic
- user-entered match statistics are self-reported and are not presented as official event-tracking data

## Scope

### Explicit non-goal

PlayerIQ does **not** perform automated video analysis or computer-vision tracking.

Also outside the capstone core:

- GPS integration
- team management
- scouting marketplace
- mobile app
- automated medical or injury assessment

## Repository structure

```text
app/
  analytics.py     deterministic football KPIs
  auth.py          password hashing and JWT authentication
  cache.py         persistent analysis cache key
  database.py      SQLAlchemy/PostgreSQL connection
  llm.py           Groq integration and structured validation
  main.py          FastAPI endpoints
  models.py        database models
  reports.py       PDF report generator
  schemas.py       Pydantic request/response schemas
scripts/
  seed_demo.py     synthetic stranger-runnable demo data
docs/
  M1-one-pager.md
My 10x Solution - Haider Humayon.md
compose.yaml
Dockerfile
requirements.txt
```

## Development milestones

- `M1: define PlayerIQ problem and capstone scope`
- `M2: build API and PostgreSQL walking skeleton`
- `M3.1: add authentication and user data isolation`
- `M3.2: add deterministic performance intelligence`
- `M3.3: add validated AI performance analyst`
- `M3.4: add persistent AI analysis caching`
- `M3.5: add professional PDF performance reports`
- `M4: make PlayerIQ stranger-runnable`
- `M5: package capstone submission`

## Data philosophy

PlayerIQ does not decide whether a footballer is simply "good" or "bad."

It turns performance into **evidence: statistics, trends, and measurable development**.
