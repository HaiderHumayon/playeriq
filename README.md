# PlayerIQ

**Football performance intelligence built around evidence, not vague labels.**

PlayerIQ is a backend capstone project for competitive footballers who want to record performances, calculate meaningful statistics, understand trends, receive grounded AI analysis, and generate professional reports.

> "There is an epidemic failure within the game to understand what is really happening." - *Moneyball*

PlayerIQ applies that data-driven philosophy to individual football development.

## Core principle

**PlayerIQ does not decide whether a footballer is simply "good" or "bad." It turns performance into evidence: statistics, trends, and measurable development.**

**Record -> Measure -> Compare -> Understand -> Improve**

## 10x claim

PlayerIQ turns **20-30 minutes of subjective manual performance review** into a **data-backed player analysis and professional report in under two minutes**.

## Capstone concepts

| Concept | Where it lives | Status |
|---|---|---|
| API endpoints | `app/main.py` | Implemented |
| Database | `app/database.py`, `app/models.py` | Implemented |
| Authentication | `app/auth.py`, `/auth/*`, protected performance routes | Implemented |
| LLM integration | `app/llm.py`, `POST /analysis/performance` | Implemented |
| Caching | pp/cache.py, PostgreSQL i_analyses cache | Implemented |
| PDF reporting | planned M3 | Planned |

No swaps are planned.

## M2 walking skeleton

The first working slice is:

```text
POST /performances -> validation -> PostgreSQL -> GET /performances
```

A Docker restart is included in the verification flow to prove the record survives a service restart.

## Run

1. Copy `.env.example` to `.env` and replace the placeholder password.
2. Start the stack:

```powershell
docker compose up -d --build
```

3. Open Swagger:

```text
http://localhost:8010/docs
```

4. Health check:

```text
http://localhost:8010/health
```

## Example performance

```json
{
  "player_name": "Demo Player",
  "match_date": "2026-08-30",
  "opponent": "Lahore FC",
  "position": "CM",
  "minutes_played": 90,
  "goals": 1,
  "assists": 1,
  "shots": 3,
  "key_passes": 4,
  "tackles": 5,
  "interceptions": 2,
  "rating": 8.2,
  "rpe": 8,
  "notes": "Strong second half and created several chances."
}
```

## Scope

The capstone core stays limited to five product features:

1. player account
2. performance logging
3. performance history and trends
4. AI Performance Analyst
5. PDF Performance Report

### Explicit non-goal

Automated video analysis and computer-vision tracking are outside the capstone scope.

See [`docs/M1-one-pager.md`](docs/M1-one-pager.md) for the full M1 plan.

## Authentication

PlayerIQ uses password-based accounts with signed JWT access tokens.

Endpoints:

- `POST /auth/register` - create a player account
- `POST /auth/login` - log in and receive a bearer token
- `GET /auth/me` - read the authenticated profile
- `POST /performances` - protected; the player identity comes from the token
- `GET /performances` - protected; returns only the current user's records

Passwords are never stored directly. PlayerIQ stores a salted PBKDF2-SHA256 password hash. The JWT signing secret lives only in `.env`, which is excluded from Git.

### Data isolation

Every performance row is owned by a user ID. A player cannot choose another player identity in the request body, and performance queries are filtered by the authenticated user's ID. The M3 verification creates two accounts and proves that the second account cannot see the first account's performance data.
## Performance intelligence

PlayerIQ calculates football KPIs in Python before any AI is involved.

`GET /analytics/summary?window=5` compares the latest performance window with the previous window and returns:

- minutes, goals, assists, and total goal contributions
- shots, key passes, tackles, and interceptions
- average match rating and average RPE
- goals, assists, goal contributions, shots, key passes, tackles, and interceptions per 90
- measurable trend deltas for average rating, goal contributions per 90, key passes per 90, and tackles per 90

The endpoint is authenticated and only uses the logged-in player's records.

**Evidence rule:** PlayerIQ's LLM will later interpret these verified statistics. It will not be trusted to calculate them.
## AI Performance Analyst

`POST /analysis/performance?window=5` is PlayerIQ's narrow LLM feature.

The backend first calculates the verified football KPIs with deterministic Python. Only then does the LLM interpret those numbers. The model is instructed not to invent match events, injuries, medical conclusions, scouting claims, or unsupported metrics.

The response is constrained to a structured schema and then validated again with Pydantic before it can be saved or returned.

The output contains:

- evidence-backed summary
- 2-4 strengths with numerical evidence
- 2-4 development areas with numerical evidence
- 2-4 training priorities
- confidence/data-limit note

### LLM usage and cost log

Each successful AI request stores:

- provider model
- prompt tokens
- completion tokens
- total tokens
- estimated provider-equivalent USD cost
- timestamp

The cost estimate uses the model's documented per-token list prices. A free-tier account may still have an actual billed amount of $0.

`GET /analysis/usage` returns the current player's recent usage logs.

The Groq API key is read from `.env` only and is never committed.
## Persistent AI caching

PlayerIQ avoids repeated LLM calls when the analysis inputs have not changed.

Before calling Groq, the backend creates a SHA-256 cache key from:

- the authenticated player
- the requested analysis window
- every performance record supplied to the analysis
- the selected LLM model
- the prompt version

The cache is stored in PostgreSQL with the validated AI analysis. An identical request returns the existing analysis with:

- `cached: true`
- `provider_call_made: false`
- the same `analysis_id`
- the same `cache_key`

No new LLM usage row is created on a cache hit.

If the player's performance data, model, prompt version, or analysis window changes, the hash changes and PlayerIQ creates a fresh analysis.

This makes caching persistent across API/container restarts rather than relying on process memory.