# Claims Status Notifications - Tasks

## Phase and status

- Phase: 3 - Tasks + Executive Summary
- Feature slug: `claims-status-notifications`
- Sources of truth: approved `intent.md` and approved `design.md`
- Specification status: Proposed, awaiting Phase 3 approval

## Implementation sequence

Implementation must preserve the approved design boundaries: assessment remains
unchanged, notification delivery is simulated, all data is explicitly synthetic,
and rejection support remains disabled until an approved source exists.

### Task 1 - Resolve implementation prerequisites

**Outcome:** Record approved choices for the design's unresolved implementation
decisions before product code is changed.

**Relevant files or components:** Approved specification addendum or decision
record; orchestration caller; notification API boundary.

**Dependencies:** Approved Phase 3 specification.

**Work:**

- Select the runtime workflow that supplies authoritative `previous_status` and
  stable `transition_id` values.
- Approve whether process-lifetime deduplication is sufficient for the training
  feature.
- Select one initial channel-independent or email-shaped `.invalid` contact
  representation and its deterministic validator.
- Define the trusted rejection-source configuration, or explicitly keep
  rejection disabled for the initial release.
- Decide whether notification contracts are internal or exported from the
  package public API.
- Confirm that one destination per transition is sufficient.
- Defer the external-adapter failure contract unless an external adapter is
  separately approved.

**Acceptance criteria:** Each choice is explicitly recorded; no implementation
infers a rejection rule, durable storage, real transport, multiple-recipient
fan-out, or public export. Any decision that changes the approved design returns
through specification approval before implementation.

**Traceability:** AC-4, AC-5, AC-7, AC-8, AC-9; Design: Unresolved decisions 1-7.

### Task 2 - Define immutable notification values

**Outcome:** Add the typed, immutable notification contracts defined by the
design without changing claims assessment or intake models.

**Relevant files or components:** `src/dreamguard/notifications.py` (proposed);
`SyntheticContactDestination`, `ClaimStatusChange`, `ClaimNotification`, and
`NotificationOutcome`.

**Dependencies:** Task 1 contact-shape and API-boundary decisions.

**Acceptance criteria:** Values are frozen dataclasses with the approved fields;
money is not added; notification records exclude the full claim, amount,
documents, reasons, identity, and health data; existing `Claim` and
`ClaimDecision` constructors remain unchanged.

**Traceability:** AC-6, AC-8, AC-9; Design: Notification domain, Intake and
public API impact, Security and privacy.

### Task 3 - Build the in-memory outbox boundary

**Outcome:** Provide deterministic, ordered, read-only inspection of simulated
notification records and processed transition IDs.

**Relevant files or components:** `src/dreamguard/notifications.py` (proposed);
in-memory outbox abstraction and implementation.

**Dependencies:** Task 2; Task 1 duplicate-suppression decision.

**Acceptance criteria:** Recording a transition ID and notification is one
logical operation; a repeated transition cannot append a second record; records
retain insertion order; inspection cannot mutate internal state; the API uses
`recorded`, never `sent` or `delivered`; no network or third-party dependency is
introduced.

**Traceability:** AC-1, AC-2, AC-3, AC-5, AC-8; Design: Simulated delivery and
transition registry, Duplicate suppression and ordering, Observability.

### Task 4 - Implement deterministic status mapping and templates

**Outcome:** Convert supported internal statuses into fixed, minimal,
client-facing notification content.

**Relevant files or components:** `src/dreamguard/notifications.py` (proposed);
status mapper and renderer.

**Dependencies:** Task 2.

**Acceptance criteria:** `pending_documents` maps to `pending`; `referred` and
`approved` retain their names; a `rejected` template exists but is not enabled
by mapping alone; unknown statuses are unsupported; each template contains only
the synthetic claim reference, status wording, and explicit simulated/synthetic
language; rendering is deterministic.

**Traceability:** AC-1, AC-2, AC-3, AC-4, AC-6, AC-8; Design: Status and message
contract, Rejection capability.

### Task 5 - Implement coordinator validation and orchestration

**Outcome:** Add `NotificationCoordinator.notify` with the approved validation,
suppression, mapping, rendering, and recording sequence.

**Relevant files or components:** `src/dreamguard/notifications.py` (proposed);
`NotificationCoordinator`; configured rejection-source gate.

**Dependencies:** Tasks 1-4.

**Acceptance criteria:** Validation order is missing transition data, invalid
contact, unchanged status, duplicate transition, then unsupported status;
expected non-recorded cases return the exact approved outcome codes with no
notification body and no outbox write; supported transitions append exactly
one record and return `recorded`; rejection remains `unsupported_status` unless
the approved source is configured; the coordinator never calls `assess_claim`.

**Traceability:** AC-1 through AC-8; Design: Data flow, Error behavior, Proposed
interfaces and contracts.

### Task 6 - Connect the approved transition-producing workflow

**Outcome:** Have the selected orchestration caller submit one
`ClaimStatusChange` after assessment while preserving assessment and intake
contracts.

**Relevant files or components:** Runtime workflow selected in Task 1;
`assess_claim` call site; notification coordinator boundary. Do not modify claim
JSON intake to load contact details.

**Dependencies:** Task 1 workflow decision; Task 5.

**Acceptance criteria:** The caller supplies a stable transition ID, previous
status, current decision, claim reference, and one explicitly synthetic
destination; unchanged reassessment and retries are distinguishable; contact
data remains outside `Claim` and `load_claims`; the outcome is available for
operator inspection.

**Traceability:** AC-1, AC-2, AC-3, AC-5, AC-7, AC-8, AC-9; Design: Data flow,
Intake and public API impact.

### Task 7 - Apply the approved package API decision

**Outcome:** Expose or retain notification contracts according to the decision
from Task 1 without disturbing existing exports.

**Relevant files or components:** `src/dreamguard/__init__.py` only if public
exports are approved; otherwise the internal notification module.

**Dependencies:** Tasks 1, 2, and 5.

**Acceptance criteria:** Existing exports are neither renamed nor removed; new
exports, if approved, have concise docstrings and stable names; internal-only
contracts are not accidentally re-exported.

**Traceability:** AC-9; Design: Intake and public API impact.

### Task 8 - Add focused notification unit tests

**Outcome:** Verify every notification rule and negative path with deterministic
synthetic data using `unittest`.

**Relevant files or components:** `tests/test_notifications.py` (proposed);
notification module; standard-library log capture if logging is implemented.

**Dependencies:** Tasks 2-7.

**Acceptance criteria:** Tests cover exactly one record for
`pending_documents`, `referred`, and `approved`; rejection disabled and enabled
with an approved source stub; unchanged status; duplicate and distinct
transition IDs; later return to a prior status; empty and malformed contacts;
`is_synthetic=False`; missing identifiers; unknown status; exact deterministic
content; ordered read-only inspection; exclusion of prohibited details; and
redaction of raw destinations and message bodies from logs. Test destinations
use reserved values such as `client-1001@example.invalid`.

**Traceability:** AC-1 through AC-8; Design: Testing approach, Security and
privacy, Observability.

### Task 9 - Preserve claims and intake behavior with regression tests

**Outcome:** Demonstrate that notification work has not changed assessment,
intake, money handling, or existing public behavior.

**Relevant files or components:** Existing `tests/test_claims.py`; existing
claims and intake tests; package exports.

**Dependencies:** Tasks 6 and 7.

**Acceptance criteria:** Existing tests pass unchanged; assessment still emits
only `pending_documents`, `referred`, and `approved`; no rejection rule is added;
`Claim`, `ClaimDecision`, `assess_claim`, and `load_claims` retain their approved
contracts; monetary values remain `Decimal`.

**Traceability:** AC-4, AC-9; Design: Existing claims domain, Rejection
capability.

### Task 10 - Document simulated operation and privacy limits

**Outcome:** Give training operators accurate instructions for inspecting
notification outcomes without implying real delivery.

**Relevant files or components:** `README.md` and/or `docs/SERVICE.md`; synthetic
example data only if the Task 1 workflow requires a separate fixture.

**Dependencies:** Tasks 1 and 6; implemented API behavior must be stable.

**Acceptance criteria:** Documentation calls the outbox simulated, defines all
outcome codes, explains process-lifetime deduplication, identifies rejection as
disabled or conditionally configured, and uses only explicitly fictional
`.invalid` destinations and synthetic claim references. It does not document
durability, real delivery, retries, or multi-recipient behavior unless those
capabilities receive separate approval and implementation.

**Traceability:** AC-4, AC-5, AC-7, AC-8; Design: Observability, Security and
privacy, Simulated delivery and transition registry.

### Task 11 - Run release and operational checks

**Outcome:** Produce completion evidence for behavior, compatibility, privacy,
and training operation before enabling the feature.

**Relevant files or components:** Full repository; `scripts/score.py`; operator
inspection workflow.

**Dependencies:** Tasks 2-10.

**Acceptance criteria:** `python -m unittest discover -s tests -v` passes;
`python scripts/score.py` completes and its result is reviewed; a synthetic
smoke run records one supported transition and exposes its `recorded` outcome;
an invalid contact and duplicate transition produce no additional records; no
network call occurs; source, tests, fixtures, docs, and captured logs are
reviewed for real or excessive personal, policy, health, contact, and financial
data. Rollout is limited to the training workflow and in-memory lifetime.

**Traceability:** AC-1 through AC-9; Design: Testing approach, Observability,
Security and privacy.

## Acceptance criteria traceability

| Intent criterion | Design elements | Implementation tasks | Validation |
| --- | --- | --- | --- |
| AC-1 | Pending mapping, coordinator, outbox | 3, 4, 5, 6, 8, 11 | Mapping, single-record, and smoke checks |
| AC-2 | Referred mapping, coordinator, outbox | 3, 4, 5, 6, 8, 11 | Mapping, single-record, and smoke checks |
| AC-3 | Approved mapping, coordinator, outbox | 3, 4, 5, 6, 8, 11 | Mapping, single-record, and smoke checks |
| AC-4 | Conditional rejection source and template | 1, 4, 5, 8, 9, 10, 11 | Disabled/enabled source-stub tests; no rule regression |
| AC-5 | Previous-status and transition-ID suppression | 1, 3, 5, 6, 8, 10, 11 | Unchanged, retry, revisit, and smoke checks |
| AC-6 | Minimal immutable notification and templates | 2, 4, 5, 8, 11 | Exact-content and prohibited-field tests |
| AC-7 | Contact validation and deterministic outcomes | 1, 5, 6, 8, 10, 11 | Invalid-contact outcome and zero-write checks |
| AC-8 | Synthetic marker, reserved data, redaction, no network | 1-6, 8, 10, 11 | Validation, log capture, privacy review, smoke check |
| AC-9 | Separate module and unchanged assessment/intake/API | 1, 2, 6, 7, 9, 11 | Existing suite and contract review |

## Traceability check

All intent acceptance criteria map to approved design elements, ordered
implementation tasks, and executable or review-based validation. No acceptance
criterion is omitted.

The following gaps prevent unconditional implementation and are intentionally
carried into Task 1: ownership of transition history and IDs; process-only
versus durable deduplication; concrete destination validation; rejection-source
authority; public export policy; future infrastructure-failure semantics; and
single-destination sufficiency. AC-4 remains conditional until a rejection
source is approved. Task 6 cannot target a concrete caller until workflow
ownership is selected.

The source documents' status lines still say they await Phase 1 and Phase 2
approval, although explicit approval was supplied outside those artifacts. This
is a documentation-status inconsistency, not a behavioral traceability gap; the
approved source content was not altered during Phase 3.

## Phase boundary

This artifact is an implementation and validation plan only. It does not
authorize product code, tests, a rejection assessment rule, or real delivery.
