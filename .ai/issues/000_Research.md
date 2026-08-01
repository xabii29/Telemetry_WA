# ISSUE-000 — Racing Telemetry Ecosystem Research

## Metadata

**Type:** Research / Technical Feasibility Study

**Priority:** Critical

**Sprint:** Sprint 0

**Status:** Pending

**Owner:** Research Agent

---

# Objective

Telemetry_WA is being designed as a modular telemetry framework capable of supporting multiple racing simulators through interchangeable Drivers.

Before defining the internal protocol (`TelemetryPacket`), the architecture team requires objective evidence about the current telemetry ecosystem.

This issue is NOT a software implementation task.

This issue is a technical investigation whose conclusions will directly influence the system architecture.

---

# Scope

Research at least the following games:

- Forza Motorsport (2023)
- Forza Horizon 5
- EA Sports F1
- Assetto Corsa
- Assetto Corsa Competizione
- iRacing
- Automobilista 2
- Project CARS 2
- rFactor 2
- Dirt Rally 2.0
- BeamNG.drive

Additional titles may be included if they are relevant.

---

# Research Rules

Every statement must be supported by evidence.

When information cannot be confirmed:

Use

UNKNOWN

Never invent values.

Never estimate technical capabilities.

Distinguish between:

- Official documentation
- Community documentation
- Third-party estimates
- Personal/community observations

---

# Research Tasks

## 1. Game Overview

For every game determine:

- Developer
- Release year
- Current support status
- Platforms
- Latest update (if applicable)

---

## 2. Community Analysis

Investigate:

- Estimated active players
- Steam concurrent players (if available)
- Console presence
- Esports activity
- Community size
- Modding community
- Longevity

Classify:

Very Large

Large

Medium

Small

Niche

Legacy

Support every classification with evidence.

---

## 3. Telemetry Interface

Determine:

Communication method

- UDP
- Shared Memory
- SDK
- API
- Plugin
- Other

Packet format

Typical update rate

Official documentation

Example implementations

Licensing limitations

Implementation complexity

Easy

Medium

Hard

---

## 4. Telemetry Variables

Create a comparison table.

Variables should include at least:

Vehicle

Engine

Transmission

Driver Inputs

Motion

Physics

Track

Session

Weather

Damage

Game-specific variables

For every variable classify:

Confirmed

Available

Calculated

Unavailable

Unknown

---

## 5. Existing Telemetry Ecosystem

Research:

Existing telemetry software.

Examples:

- SimHub
- MoTeC
- Race Studio
- Z1 Dashboard
- Community dashboards
- Mobile telemetry applications
- GitHub projects
- Browser dashboards

For every tool identify:

- Active?
- Popular?
- Open source?
- Main purpose

---

## 6. Market Opportunity

For every game answer:

Does the community already have mature telemetry software?

Are current tools outdated?

Would a browser-based telemetry dashboard provide value?

Would Telemetry_WA solve an existing problem?

Support every answer with evidence.

---

## 7. Driver Priority

Estimate:

Development effort

Expected number of users

Telemetry richness

Community demand

Long-term maintenance cost

Potential architectural value

---

# Deliverable

Create

docs/research/telemetry_ecosystem.md

---

# Required Structure

The document MUST contain:

1. Executive Summary

2. Comparison of telemetry interfaces

3. Variable comparison matrix

4. Existing telemetry ecosystem

5. Community analysis

6. Market opportunity

7. Driver implementation complexity

8. Priority recommendation

9. Open architectural questions

10. References

---

# References

Every important statement must include a reference.

Use preferably:

- Official documentation
- SDK documentation
- Official developer pages

Community sources may be used only when official information is unavailable.

---

# Acceptance Criteria

This issue is complete only if:

✓ At least 10 games were investigated.

✓ Every recommendation is justified.

✓ Every numerical statement has a source.

✓ A telemetry variable comparison matrix was created.

✓ Existing telemetry software was analyzed.

✓ Community demand was evaluated.

✓ Driver implementation complexity was estimated.

✓ A Version 1.0 priority list was proposed.

✓ Open architectural questions were documented.

✓ Complete references were included.

---

# Important

This is NOT a summary.

This is NOT a wiki article.

This is NOT a marketing document.

This is an engineering feasibility study.

The architecture team will use this document to decide:

- Which games deserve official support.
- Which telemetry variables belong to the core protocol.
- Which variables should become optional modules.
- Which Driver abstractions are required.
- Which platforms should be postponed after Version 1.0.

Your objective is to produce evidence that supports engineering decisions.