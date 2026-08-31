# PlayerIQ - M1 One-Pager

## Problem

Football performance is often discussed too subjectively. Players are described as "good", "bad", "in form", or "not contributing enough" without enough structured evidence behind those judgments. Match statistics, training intensity, minutes, ratings, attacking contributions, defensive actions, and performance trends are often scattered across notes, spreadsheets, or memory.

Moneyball captures the philosophy behind PlayerIQ with the line:

> "There is an epidemic failure within the game to understand what is really happening."

PlayerIQ applies that data-driven idea to individual football development. It does not simply decide whether a footballer is good or bad. It turns performance into evidence: statistics, trends, and measurable development.

Instead of saying "your recent performances were good", PlayerIQ is designed to say something measurable: your average rating increased, your attacking output changed, your defensive involvement changed, and here are the numbers behind that conclusion.

## Who has this problem

Competitive footballers, academy players, and coaches who want a structured way to record and understand individual performance without expensive professional analytics software.

## 10x claim

**PlayerIQ turns 20-30 minutes of subjective manual performance review into a data-backed player analysis and professional report in under two minutes.**

## Core principle

**PlayerIQ does not decide whether a footballer is simply "good" or "bad." It turns performance into evidence: statistics, trends, and measurable development.**

Product flow:

**Record -> Measure -> Compare -> Understand -> Improve**

## Core features

1. Player account and protected personal data.
2. Match and training performance logging.
3. Performance history, calculated KPIs, and trends.
4. AI Performance Analyst grounded in verified statistics.
5. Downloadable professional player performance report.

## Program concepts

PlayerIQ will implement six primary program concepts, with no swaps:

| Concept | Planned implementation |
|---|---|
| API endpoints | FastAPI performance, analytics, AI, and report endpoints |
| Database | PostgreSQL persistence |
| Authentication | Protected user routes |
| LLM integration | Narrow AI performance analysis over verified statistics |
| Caching | Reuse AI analyses when the underlying performance data is unchanged |
| PDF reporting | Generate player performance reports |

## Non-goal

PlayerIQ will **not** perform automated video analysis or computer-vision tracking.

Video analysis, GPS integrations, team dashboards, scouting marketplaces, and mobile apps are future ideas, not part of the capstone core.
