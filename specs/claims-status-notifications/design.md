# Design: Claim Status Notifications

## Overview

Add a lightweight notification concept that can describe the outcome of a claim assessment without changing the existing rule engine. The design should make the result of `assess_claim()` easier to consume in documentation, tests, and future integrations while preserving the current public API.

## Current Baseline

The current implementation already exposes:

- `Claim`: an immutable input model with policy number, claim type, amount, months active, and documents.
- `ClaimDecision`: an immutable output model with `status`, `approved_amount`, and `reasons`.
- `assess_claim(claim: Claim) -> ClaimDecision`: a deterministic function that applies the assessment rules in a fixed order.

The feature should build on these existing types rather than replace them.

## Proposed Design

### 1. Add a notification message concept

Introduce an optional helper concept that produces a human-readable notification string for each `ClaimDecision` outcome. This is a design-only addition for the specification phase and should not break the current public API.

Suggested shape for the implementation plan:

- A small helper function such as `build_notification_message(claim: Claim, decision: ClaimDecision, contact: ClientContact | None = None) -> str`
- The helper returns a client-safe message describing the final outcome based on the claim status
- The message should use the same synthetic values as the current examples and may include a fictional contact name, email, and phone number

### Notification contract

The design should define a clear client-facing notification contract that:

- uses only fictional contact details
- identifies the claim by policy number
- states the final outcome as approved, pending documents, referred, or rejected
- provides a clear follow-up path through synthetic contact details when available

This contract should be explicit enough that the implementation, docs, and tests all agree on the wording and behavior.

### 2. Keep the existing decision model intact

Do not change the existing public API surface of:

- `Claim`
- `ClaimDecision`
- `assess_claim()`
- `load_claims()`

The new notification capability should be additive and documented as a helper or future extension, rather than a breaking change.

### 3. Use the existing assessment outcomes

The notification text should be derived from the current `ClaimDecision.status` values:

- `approved`: "Claim approved for the requested amount."
- `rejected`: "Claim rejected because the claim did not satisfy the required rules."
- `referred`: "Claim referred for review because the waiting period has not been completed."
- `pending_documents`: "Claim is pending documents because required documents are missing."

This keeps the design aligned with the current assessment rules and provides a stable contract for future use.

## Behavioral Rules

The proposed notification behavior should follow these rules:

1. The notification is based on the current decision produced by `assess_claim()`.
2. The notification does not change the existing status or approved amount.
3. The notification is deterministic for the same claim and decision.
4. The message should be suitable for documentation, demos, and simple user-facing explanations.
5. The feature should continue to work only with synthetic examples and fictional records.

## Integration Points

The design integrates with the existing DreamGuard flow as follows:

- `Claim` remains the input object.
- `assess_claim()` remains the authority for decision generation.
- `ClaimDecision` remains the output object.
- A notification helper can be called after assessment to explain the decision.

## Testing Expectations

The implementation should add or extend unit tests to verify:

- an approved claim produces the expected notification text
- a rejected claim produces the expected notification text
- a referred claim produces the expected notification text
- a pending-documents claim produces the expected notification text
- synthetic contact details are included when provided
- the package exports the notification helper and any contact model correctly

Tests should continue to use the existing `unittest` style already present in `tests/test_claims.py`.

## Documentation Impact

The feature should be reflected in:

- `docs/SERVICE.md`
- the public docstrings for any newly added helper function

## Notes

This design is intentionally additive and does not alter the fixed assessment rules already documented in the project instructions.
