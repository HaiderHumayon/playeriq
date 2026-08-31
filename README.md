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
| Authentication | pp/auth.py, /auth/*, protected performance routes | Implemented |
| LLM integration | planned M3 | Planned |
| Caching | planned M3 | Planned |
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