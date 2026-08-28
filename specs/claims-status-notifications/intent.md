# Intent: Claim Status Notifications

## Summary

Add a feature that allows DreamGuard to produce a clear status notification for each claim assessment outcome. The feature should make the result of `assess_claim()` easier to understand and trace in downstream workflows, while preserving the existing public API and business rules.

## Problem Statement

DreamGuard currently returns a `ClaimDecision` with `status`, `approved_amount`, and `reasons`, but there is no structured way to describe the transition or outcome in a human-friendly form. This makes it harder to explain the result of a claim assessment in docs, tests, and future integrations.

## Goals

- Provide a clear, documented specification for notifying users about a claim status outcome.
- Keep the change aligned with the existing DreamGuard assessment flow.
- Preserve the current public API and the existing assessment rules.
- Use synthetic example data only.
- Define a client-facing notification contract that uses synthetic contact details and covers pending, referred, approved, and rejected outcomes.
- Make the public API and documentation expectations explicit so the feature can be traced from intent to implementation.

## Success Criteria

- The feature is described clearly enough for implementation.
- The design can be traced to the current `Claim` and `ClaimDecision` models.
- The proposed change does not alter the existing assessment rule order or public API contract.
- The specification explicitly covers synthetic contact details, client-facing notification content, public API exposure, and validation expectations.

## Constraints and Assumptions

- The assessment rules in `assess_claim()` remain unchanged unless the specification explicitly calls for a new behavior.
- The feature should be compatible with the current `dreamguard` package structure.
- All example values remain fictional and synthetic.
- The feature is intended for educational and training purposes, not production use.

## Dependencies

- Existing `Claim` and `ClaimDecision` dataclasses in `src/dreamguard/claims.py`
- Existing `assess_claim()` behavior
- Existing documentation in `docs/SERVICE.md`
