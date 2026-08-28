# Claims Status Notifications - Executive Summary

## Status

- Phase: 3 - Tasks + Executive Summary
- Feature slug: `claims-status-notifications`
- Basis: approved intent and design
- Specification status: Proposed, awaiting Phase 3 approval

## Problem and expected outcome

DreamGuard can deterministically assess synthetic claims, but it has no way to
make status outcomes observable as client notifications. The approved feature
will produce one inspectable, simulated notification when an eligible synthetic
claim transitions to pending, referred, or approved. Rejected presentation is
defined but remains unavailable until an authoritative rejection source is
separately approved.

The expected outcome is a deterministic training capability that communicates
minimal status information to one explicitly synthetic destination, suppresses
unchanged reassessments and retried transitions, and gives operators precise
outcomes without claiming that a real message was delivered.

## Approved scope

- Add a notification boundary beside the existing assessment domain.
- Preserve `Claim`, `ClaimDecision`, `assess_claim`, `load_claims`, current
  assessment statuses, money handling, and existing public exports.
- Map `pending_documents` to client-facing `pending`; support `referred` and
  `approved`; gate `rejected` on an approved source.
- Validate one explicitly synthetic contact destination and reject invalid or
  non-synthetic destinations deterministically.
- Record minimal immutable notifications in an ordered in-memory outbox.
- Suppress unchanged statuses and duplicate transition IDs for the lifetime of
  an outbox instance.
- Use only standard-library implementation and `unittest` tests with explicitly
  fictional data.

Real transport, production data, a rejection assessment rule, durable storage,
cross-process idempotency, multi-recipient fan-out, provider retries, and
production security controls are outside the approved scope.

## Proposed design

An orchestration caller detects a status transition after `assess_claim` and
supplies a stable transition ID, previous status, current `ClaimDecision`,
synthetic claim reference, and separate synthetic destination. A
`NotificationCoordinator` validates this input in a fixed order, suppresses
unchanged or duplicate transitions, maps the status, renders a fixed minimal
template, and atomically records the transition and notification in an
in-memory outbox.

Every call returns one operator-facing outcome: `recorded`,
`unchanged_status`, `duplicate_transition`, `invalid_contact`,
`invalid_transition`, or `unsupported_status`. Non-recorded outcomes expose no
notification body. Inspection and optional logs avoid raw destinations,
message bodies, claim amounts, documents, reasons, identity, and health data.

## Delivery approach

Delivery starts by resolving the approved design's implementation prerequisites,
then adds immutable notification values, the in-memory outbox, deterministic
mapping and templates, and coordinator behavior. The selected runtime workflow
is integrated only after its ownership of transition identity is approved.
Focused `unittest` coverage verifies every status, suppression case, validation
outcome, privacy exclusion, and rejection gate. Existing regression tests,
documentation, the challenge score, and synthetic operational smoke checks form
the completion gate.

Rollout is restricted to the DreamGuard training workflow and process-lifetime
in-memory state. A `recorded` outcome means accepted by the simulated outbox,
not sent or delivered.

## Major risks and controls

- **Unapproved rejection behavior:** Keep assessment unchanged and reject the
  status unless an approved source is configured.
- **Duplicate notifications:** Compare previous and current status and register
  stable transition IDs atomically with outbox records.
- **Privacy leakage:** Require explicit synthetic markers, use reserved
  `.invalid` examples, minimize message fields, and redact logs.
- **Misleading delivery claims:** Use `recorded` terminology and document the
  outbox as simulated.
- **Compatibility regressions:** Keep contact and notification state outside
  claims intake and run the full existing test suite.
- **Restart or concurrency assumptions:** State that the initial outbox is
  process-local, non-durable, and does not claim concurrency safety.

## Unresolved decisions

Implementation requires decisions on the authoritative transition-producing
workflow, adequacy of process-lifetime deduplication, initial destination shape
and validator, rejection-source authority, public versus internal notification
APIs, and single-destination sufficiency. Failure semantics for a future durable
or external adapter remain deferred because no such adapter is approved.

Until these decisions are recorded, rejection enablement and concrete runtime
integration remain blocked. Decisions that alter the approved architecture or
scope require a specification update and approval.

## Traceability result

All nine intent acceptance criteria are represented in the approved design and
mapped in `tasks.md` to implementation outcomes and validation evidence. AC-4
is deliberately conditional on approval of a rejection source; no rejection
rule is authorized. The unresolved design decisions are preserved as Task 1
prerequisites rather than converted into unsupported assumptions.

One documentation-status inconsistency remains: the approved `intent.md` and
`design.md` still describe themselves as awaiting their respective approvals.
The approvals were explicitly supplied outside those files. This does not leave
an acceptance criterion, design element, or implementation task untraced.
