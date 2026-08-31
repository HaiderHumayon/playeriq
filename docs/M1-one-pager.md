# PlayerIQ - M1 One-Pager

## Problem

Football performance is often discussed too subjectively. Players are described as "good", "bad", "in form", or "not contributing enough" without enough structured evidence behind those judgments. Match statistics, minutes, ratings, attacking contributions, defensive actions, and performance trends are often scattered across notes, spreadsheets, or memory.

PlayerIQ follows a Moneyball-style principle: use measurable evidence before broad judgments. It applies that data-driven idea to individual football development.

Instead of saying "your recent performances were good", PlayerIQ is designed to say something measurable: your average rating changed, your attacking output changed, your defensive involvement changed, and here are the numbers behind that conclusion.

## Who has this problem

Competitive footballers, academy players, and coaches who want a structured way to record and understand individual performance without expensive professional analytics software.

## 10x claim

**Target: PlayerIQ turns a 20-30 minute subjective manual performance review into a data-backed player analysis and professional report in under two minutes for a prepared player dataset.**

## Core principle

**PlayerIQ does not decide whether a footballer is simply "good" or "bad." It turns performance into evidence: statistics, trends, and measurable development.**

Product flow:

**Record -> Measure -> Compare -> Understand -> Improve**

## Core features

1. Player account and protected personal data.
2. Match performance logging.
3. Performance history, calculated KPIs, and trends.
4. AI Performance Analyst grounded in verified statistics.
5. Downloadable professional player performance report.

## Program concepts

PlayerIQ implements six primary program concepts, with no swaps:

| Concept | Implementation |
|---|---|
| API endpoints | FastAPI performance, analytics, AI, and report endpoints |
| Database | PostgreSQL persistence |
| Authentication | Protected user routes and user-level ownership |
| LLM integration | Narrow AI performance analysis over verified statistics |
| Caching | Reuse AI analyses when the underlying inputs are unchanged |
| PDF reporting | Generate player performance reports |

## Non-goal

PlayerIQ will **not** perform automated video analysis or computer-vision tracking.

GPS integration, team dashboards, scouting marketplaces, mobile apps, and automated medical assessment are outside the capstone core.
