# Summary: Claim Status Notifications

## Implemented outcome

The DreamGuard package now exposes a small, additive notification helper that turns an assessment decision into a clear human-readable message. The behavior is grounded in the current assessment status values and does not change the existing decision rules or public API contract for `Claim`, `ClaimDecision`, `assess_claim()`, or `load_claims()`.

## What changed

- Added `build_notification_message(claim, decision)` to the claims module.
- Exported the helper from the package entry point.
- Documented the new helper in `docs/SERVICE.md`.
- Added unit tests covering approved, rejected, referred, and pending-documents outcomes.

## Notes

The implementation remains focused on the synthetic training scenario and preserves the repository’s existing conventions around deterministic behavior and fictional data.

A dedicated traceability review artifact is also available in [specs/claims-status-notifications/review.md](specs/claims-status-notifications/review.md).
