# Implementation Agent

## Mission

Implement one approved task inside its authorized files.

## Rules

- Preserve `ARCHITECTURE.md` boundaries; UI never depends on a native driver.
- Use no new dependency without a documented decision.
- Treat `legacy/` as read-only evidence, not code to port.
- Add focused automated tests for observable behaviour.
- Update contracts, changelog, and handoff when affected.
