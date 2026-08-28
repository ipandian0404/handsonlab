# Claims Status Notifications - Design

## Phase and status

- Phase: 2 - Design
- Feature slug: `claims-status-notifications`
- Source of truth: approved `intent.md`
- Specification status: Proposed, awaiting Phase 2 approval

## Design overview

Add a notification orchestration boundary beside, not inside, claims assessment.
The boundary accepts an already-produced `ClaimDecision`, an explicit status
transition identifier, and one synthetic contact destination. It maps supported
internal statuses to client-facing statuses, validates that the destination is
synthetic, suppresses unchanged or previously processed transitions, renders a
minimal notification, and records it in a simulated in-memory outbox.

The existing `Claim`, `ClaimDecision`, `assess_claim`, and `load_claims`
contracts remain unchanged. In particular, assessment continues to produce only
`pending_documents`, `referred`, and `approved`. Rejected notifications remain a
conditional capability and do not add or imply a rejection assessment rule.

## Architecture and responsibilities

### Existing claims domain

The claims domain remains responsible only for deterministic assessment:

- `Claim` remains the immutable assessment input.
- `ClaimDecision` remains the immutable assessment result.
- `assess_claim` preserves its current rule ordering and outputs.
- `pending_documents` remains the internal status; notification presentation
  maps it to the client-facing status `pending`.
- No contact, transition history, or delivery behavior is added to `Claim` or
  `assess_claim`.

This preserves AC-9 and prevents notification concerns from changing assessment
outcomes.

### Notification domain

A proposed notification module owns immutable values and orchestration:

- `SyntheticContactDestination` contains one channel-independent destination
  string and an explicit `is_synthetic` marker. The initial design supports one
  destination per transition.
- `ClaimStatusChange` contains a unique `transition_id`, the synthetic claim
  reference, the previous internal status or `None`, the current
  `ClaimDecision`, and the destination.
- `ClaimNotification` is the minimal record prepared for the outbox. It contains
  the transition ID, synthetic claim reference, destination, client-facing
  status, subject, and body. It excludes claim amount, documents, reasons,
  identity, health details, and the full `Claim` object.
- `NotificationOutcome` reports a deterministic result code and, when created,
  the notification record. It is the operator-facing observation boundary.
- `NotificationCoordinator` validates, maps, renders, deduplicates, and records
  notifications. It never assesses a claim.

### Simulated delivery and transition registry

The initial delivery boundary is an in-memory outbox. It stores notification
records and processed transition IDs for deterministic inspection in tests and
training workflows. Recording a transition ID and its notification must be one
logical operation so retrying the same transition cannot create a second outbox
record.

This boundary simulates acceptance for delivery; it does not claim that a real
message was sent. Its state lasts only for the lifetime of the outbox instance.
Durable suppression across process restarts is intentionally unresolved because
the repository has no persistence mechanism.

The storage boundary should be replaceable by a durable outbox later without
changing assessment or notification mapping contracts.

### Rejection capability

The status mapper defines `rejected` presentation content, but the coordinator
must not enable that path by default. Rejected notification processing requires
an explicitly configured, approved rejection decision source identifier. When
none is configured, a `ClaimDecision` with status `rejected` produces
`unsupported_status` and no outbox record.

The source is responsible for producing the rejection decision. This feature
does not define a rejection rule, modify `assess_claim`, or infer rejection from
amounts, claim types, documents, or reasons. Enabling a rejection source is a
separate approval prerequisite for AC-4.

## Proposed interfaces and contracts

Names below define behavioral contracts for later implementation; they are not
current public APIs.

```python
@dataclass(frozen=True)
class SyntheticContactDestination:
    value: str
    is_synthetic: bool


@dataclass(frozen=True)
class ClaimStatusChange:
    transition_id: str
    claim_reference: str
    previous_status: str | None
    decision: ClaimDecision
    destination: SyntheticContactDestination


@dataclass(frozen=True)
class ClaimNotification:
    transition_id: str
    claim_reference: str
    destination: SyntheticContactDestination
    client_status: str
    subject: str
    body: str


@dataclass(frozen=True)
class NotificationOutcome:
    code: str
    notification: ClaimNotification | None


class NotificationCoordinator:
    def notify(self, change: ClaimStatusChange) -> NotificationOutcome: ...
```

The proposed outcome codes are:

| Code | Meaning | Outbox write |
| --- | --- | --- |
| `recorded` | A supported transition was accepted by the simulated outbox. | One |
| `unchanged_status` | Previous and current internal statuses are equal. | None |
| `duplicate_transition` | The transition ID was already processed. | None |
| `invalid_contact` | The destination is empty, malformed, or not explicitly synthetic. | None |
| `invalid_transition` | Required transition or claim reference data is absent. | None |
| `unsupported_status` | The status is unknown, or rejection has no approved source. | None |

`notify` returns outcomes rather than raising for expected validation and
suppression cases. Programmer errors that violate constructor types may raise
standard Python exceptions. Outbox infrastructure failures are not represented
as successful delivery; their exact exception-versus-outcome contract remains
an unresolved decision for a future durable transport.

## Status and message contract

| Internal decision status | Client-facing status | Current support | Message meaning |
| --- | --- | --- | --- |
| `pending_documents` | `pending` | Existing assessment path | The synthetic claim is pending and further information is required. |
| `referred` | `referred` | Existing assessment path | The synthetic claim was referred for review. |
| `approved` | `approved` | Existing assessment path | The synthetic claim was approved. |
| `rejected` | `rejected` | Conditional | The synthetic claim was rejected, only when supplied by an approved rejection source. |

Each message includes only the synthetic claim reference and client-facing
status wording. It does not include decision reasons or approved amounts in the
initial design. Templates are fixed by status so rendering is deterministic.
The message must state that the record and destination are synthetic and that
the outbox represents simulated notification delivery.

Example destination data must use reserved, non-routable values such as
`client-1001@example.invalid`; no real destination may be accepted merely
because it is syntactically valid.

## Data flow

1. Existing code loads or constructs a synthetic `Claim` and calls
   `assess_claim`; this behavior is unchanged.
2. An orchestration caller detects a transition and constructs a
   `ClaimStatusChange` with a stable unique transition ID, previous status,
   decision, and explicitly synthetic destination.
3. The coordinator validates required identifiers and the synthetic contact
   marker.
4. If previous and current statuses match, it returns `unchanged_status`.
5. If the transition ID was processed, it returns `duplicate_transition`.
6. The coordinator maps the internal status. `rejected` is accepted only when
   an approved rejection source is configured; other unknown statuses are
   unsupported.
7. A fixed template renders a minimal immutable notification.
8. The simulated outbox atomically records the transition ID and notification.
9. The coordinator returns `recorded`; the operator inspects the outcome and
   outbox rather than interpreting a record as real-world delivery.

The caller, not `assess_claim`, owns transition detection. The current
repository has no authoritative workflow that can supply previous status or a
transition ID, so integrating that caller remains an explicit unresolved
decision.

## Duplicate suppression and ordering

- Equality of `previous_status` and `decision.status` suppresses an unchanged
  reassessment.
- A unique `transition_id` suppresses retries of the same transition.
- Different transition IDs may legitimately produce later notifications,
  including a later return to a previously seen status.
- Duplicate checks occur before rendering and recording.
- A single outbox instance provides deterministic insertion order for operator
  inspection.
- The in-memory design does not claim concurrency safety or restart durability;
  those guarantees must be defined before a concurrent or persistent adapter is
  approved.

## Intake and public API impact

Contact data must not be added to existing claim JSON records or parsed by
`load_claims`. A later orchestration boundary may load a separate synthetic
contact fixture, but its schema and ownership require approval. Keeping contact
outside claim intake avoids coupling communication details to the immutable
domain model.

No existing export is renamed or removed. Whether notification contracts become
exports from `dreamguard.__init__` is unresolved; later implementation must make
that compatibility decision explicitly.

## Error behavior

- Empty transition IDs or claim references return `invalid_transition`.
- Empty destination values, values failing the selected channel validator, or
  destinations without `is_synthetic=True` return `invalid_contact`.
- An unchanged status returns `unchanged_status`, even if it has not previously
  been recorded.
- A repeated transition ID returns `duplicate_transition` and does not append.
- Unknown statuses return `unsupported_status`.
- `rejected` returns `unsupported_status` unless an approved rejection source is
  configured.
- Expected non-recorded outcomes expose no message body, preventing misleading
  evidence that delivery was attempted.

Validation order is the order above: required transition data, contact,
unchanged status, duplicate transition, then status support. This makes outcomes
repeatable for inputs with more than one defect.

## Security and privacy

- Only explicitly synthetic contacts and claim references are accepted.
- Fixtures and examples use reserved fictional values, including `.invalid`
  domains where email-shaped data is needed.
- Notifications exclude amounts, documents, assessment reasons, health details,
  identity details, and full contact profiles.
- Outcomes and logs must not emit more than transition ID, result code,
  client-facing status, and a redacted destination identifier.
- The in-memory outbox must be described as simulated; no network transport or
  third-party dependency is introduced.
- Production routing, credentials, retries, retention, access controls, and
  encryption are outside this training design and require a separate review.

## Observability

Each call returns one outcome code. The in-memory outbox exposes read-only
inspection of ordered notification records and a count for tests and training
operators. Optional standard-library logging may record the transition ID,
outcome code, and client-facing status, but never the message body or raw
destination. No telemetry dependency is required.

The observable distinction is between `recorded` in a simulated outbox and no
record due to validation, suppression, or unsupported status. The design makes
no `sent` or `delivered` claim.

## Testing approach

Later implementation should use `unittest` and synthetic values only. Focused
unit tests should cover:

- one recorded notification for each of `pending_documents`, `referred`, and
  `approved`, including exact client-facing mapping;
- conditional `rejected` behavior both disabled and enabled with an approved
  source stub, without adding an assessment rule;
- unchanged-status suppression and repeated-transition suppression;
- distinct transition IDs that revisit a status;
- empty, malformed, and not-explicitly-synthetic destinations;
- unknown statuses and missing identifiers;
- minimal content, deterministic templates, and exclusion of reasons, amounts,
  documents, health details, and raw destinations from logs;
- preservation of all existing assessment and intake tests.

An in-memory fake is the initial outbox itself, so tests require no network,
clock, random value, or third-party package. Full repository tests and the
challenge score command remain completion checks for a later implementation
phase.

## Key design decisions and alternatives

### Keep assessment pure

**Decision:** Notify from a separate coordinator after assessment.

**Alternative:** Send from `assess_claim`. Rejected because it would combine a
pure deterministic rule function with contact validation, state, and delivery.

### Keep contact outside `Claim`

**Decision:** Pass a separate synthetic destination in the status-change input.

**Alternative:** Add contact fields to `Claim` or claim JSON. Rejected because
contact is not needed for assessment and would change existing constructors and
intake contracts.

### Start with a simulated outbox

**Decision:** Record notifications in memory and report `recorded`.

**Alternatives:** Email, SMS, or a third-party provider. Deferred because no
channel is approved and real delivery conflicts with the training and synthetic
data constraints. A file-backed outbox was also deferred because retention,
concurrency, and privacy behavior are unspecified.

### Identify transitions explicitly

**Decision:** Require previous status and a caller-supplied stable transition
ID. This distinguishes unchanged reassessment, retry, and a legitimate later
return to the same status.

**Alternatives:** Deduplicate by claim and status forever, which would suppress
valid later transitions; or let the coordinator infer history, which would
silently introduce persistence ownership.

### Keep rejection conditional

**Decision:** Define presentation support but gate it on an approved source.

**Alternative:** Add a rejection rule to `assess_claim`. Rejected because the
approved intent explicitly does not define one.

## Acceptance criteria traceability

| Intent criterion | Design coverage | Verification concept |
| --- | --- | --- |
| AC-1 | `pending_documents` maps to one recorded `pending` notification. | Mapping and outbox-count unit test. |
| AC-2 | `referred` maps to one recorded `referred` notification. | Mapping and outbox-count unit test. |
| AC-3 | `approved` maps to one recorded `approved` notification. | Mapping and outbox-count unit test. |
| AC-4 | `rejected` template exists but is gated on an approved source. | Disabled/enabled source-stub tests. |
| AC-5 | Previous-status equality and transition-ID registry suppress duplicates. | Unchanged and retry unit tests. |
| AC-6 | Minimal immutable record and fixed templates exclude unnecessary details. | Exact-content and exclusion tests. |
| AC-7 | Validation returns deterministic outcomes and never writes invalid contacts. | Invalid-contact outcome and count tests. |
| AC-8 | Explicit synthetic marker, reserved examples, redacted logging, no network. | Validation, fixture review, and log-capture tests. |
| AC-9 | Existing assessment models, rules, intake, and exports remain unchanged. | Existing regression suite plus status tests. |

## Unresolved decisions

1. What runtime workflow owns claim history and supplies authoritative
   `previous_status` and stable `transition_id` values?
2. Is in-process duplicate suppression sufficient for the training feature, or
   must a durable outbox preserve idempotency across restarts?
3. Which concrete contact shape and validator should the initial simulated
   channel use? The design recommends one email-shaped `.invalid` destination,
   but the channel is not approved by intent.
4. What approved component may identify itself as a rejection decision source,
   and how is that capability configured without allowing arbitrary callers to
   enable it?
5. Should the proposed notification types and coordinator become public package
   exports or remain an internal orchestration API?
6. For a future durable or external adapter, should unavailable delivery return
   a `delivery_failed` outcome or raise an infrastructure exception, and what
   retry policy applies?
7. Is one destination per transition sufficient, or must fan-out to multiple
   recipients or channels be designed before implementation?

## Phase boundary

This artifact defines the proposed architecture and contracts only. It does not
implement product code or tests and does not authorize a rejection assessment
rule. Implementation tasks and the executive summary belong to Phase 3 and must
not begin until this design is explicitly approved.