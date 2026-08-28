# Claims Status Notifications - Implementation Tasks

## Phase and status

- Phase: 3 - Tasks + Executive Summary
- Feature slug: `claims-status-notifications`
- Source of truth: approved `design.md`
- Status: Ready for implementation

---

## Implementation Tasks

### TASK-001: Implement SyntheticContactDestination data model

**Description:**  
Create the immutable `SyntheticContactDestination` class with a string value and explicit `is_synthetic` flag.
This is a foundational model representing a validated, synthetic contact channel-independent destination.

**Acceptance Criteria:**
- Class is defined as `@dataclass(frozen=True)` in `src/dreamguard/notifications.py`
- Has attributes: `value: str` and `is_synthetic: bool`
- Is importable from `dreamguard.notifications`
- Immutable (no modification after creation)
- Type hints are complete per project standards
- Module has docstring explaining synthetic-only nature

**Dependencies:** None

**Effort:** XS (< 0.5 day)

---

### TASK-002: Implement ClaimStatusChange and ClaimNotification data models

**Description:**  
Create immutable `ClaimStatusChange` input and `ClaimNotification` outbox record classes.
`ClaimStatusChange` captures a transition with identifiers, previous status, decision, and destination.
`ClaimNotification` represents the minimal record prepared for simulated delivery.

**Acceptance Criteria:**
- `ClaimStatusChange` includes: `transition_id: str`, `claim_reference: str`, `previous_status: str | None`, `decision: ClaimDecision`, `destination: SyntheticContactDestination`
- `ClaimNotification` includes: `transition_id: str`, `claim_reference: str`, `destination: SyntheticContactDestination`, `client_status: str`, `subject: str`, `body: str`
- Both are `@dataclass(frozen=True)`
- Both importable from `dreamguard.notifications`
- Type hints are complete
- Module docstring explains that all data is synthetic

**Dependencies:** TASK-001, requires `ClaimDecision` to be importable (already exists)

**Effort:** S (0.5–1 day)

---

### TASK-003: Implement NotificationOutcome data model

**Description:**  
Create immutable `NotificationOutcome` class representing the deterministic result of notification processing.
Includes a result code and an optional notification record. Defines all six outcome codes.

**Acceptance Criteria:**
- Class is `@dataclass(frozen=True)` with `code: str` and `notification: ClaimNotification | None`
- Outcome codes are documented or constants: `recorded`, `unchanged_status`, `duplicate_transition`, `invalid_contact`, `invalid_transition`, `unsupported_status`
- Importable from `dreamguard.notifications`
- Type hints are complete
- Docstring or module-level comment explains each code's meaning

**Dependencies:** TASK-002 (requires `ClaimNotification`)

**Effort:** S (0.5–1 day)

---

### TASK-004: Implement status mapping and message templates

**Description:**  
Create deterministic mapping from internal assessment statuses (`pending_documents`, `referred`, `approved`)
to client-facing statuses (`pending`, `referred`, `approved`) and define fixed message templates for each.
Optionally define `rejected` template for conditional future use (rejection source disabled by default).

**Acceptance Criteria:**
- Mapping constants or function maps internal status → client-facing status
- Templates defined for `pending_documents` → subject/body, `referred` → subject/body, `approved` → subject/body
- Each template includes claim reference placeholder and states that record/destination/outbox are synthetic
- No real email addresses or identities in example templates
- Templates are deterministic (no randomness)
- Optional: `rejected` template defined but not enabled by default
- Function or class to render templates with claim reference and client status

**Dependencies:** None (foundational)

**Effort:** S (0.5–1 day)

---

### TASK-005: Implement contact validation logic

**Description:**  
Implement validation of `SyntheticContactDestination` to ensure it is explicitly marked synthetic,
non-empty, and well-formed. Reject real-looking addresses and non-synthetic markers.

**Acceptance Criteria:**
- Validation function returns `True` for valid synthetic destinations, `False` otherwise
- Rejects empty destination values
- Rejects destinations with `is_synthetic=False`
- Accepts only destinations with `is_synthetic=True`
- Optionally validates format (e.g., email-shaped data must use `.invalid` reserved domain)
- Includes docstring with acceptance rules and example synthetic values

**Dependencies:** TASK-001 (requires `SyntheticContactDestination`)

**Effort:** S (0.5–1 day)

---

### TASK-006: Implement NotificationCoordinator orchestration logic

**Description:**  
Create the core `NotificationCoordinator` class implementing deterministic validation, deduplication,
status mapping, template rendering, and recording. No state persistence; coordinate all operations
atomically. Handle all six outcome codes and validation order.

**Acceptance Criteria:**
- Class has `notify(self, change: ClaimStatusChange) -> NotificationOutcome` method
- Performs validation in documented order: required data → contact → unchanged status → duplicate transition → status support
- Returns appropriate outcome code for each validation failure
- Maps internal status to client-facing status using templates
- Renders immutable `ClaimNotification` for supported transitions
- Atomically records transition ID and notification (no partial writes)
- Handles `rejected` status as `unsupported_status` when no rejection source configured
- Returns outcome with or without notification record per design
- Type hints complete per standards
- Docstring explains orchestration flow and outcome semantics

**Dependencies:** TASK-002, TASK-003, TASK-004, TASK-005

**Effort:** M (1–2 days)

---

### TASK-007: Implement in-memory NotificationOutbox storage and deduplication

**Description:**  
Create an in-memory outbox storing recorded notifications and processed transition IDs.
Provide atomic write operation and read-only inspection for tests/training.
Maintain deterministic insertion order.

**Acceptance Criteria:**
- Class `NotificationOutbox` with `record(transition_id: str, notification: ClaimNotification) -> None` method
- Recording is atomic: transition ID and notification together, or neither
- Raises exception if attempting to record duplicate transition ID
- Provides read-only access: `get_notifications() -> tuple[ClaimNotification, ...]` (ordered)
- Provides `has_transition(transition_id: str) -> bool` for duplicate detection
- Provides `count() -> int` for test assertions
- Includes clear docstring that this is simulated delivery and state is ephemeral
- Type hints complete

**Dependencies:** TASK-002 (requires `ClaimNotification`)

**Effort:** S (0.5–1 day)

---

### TASK-008: Integrate NotificationCoordinator with NotificationOutbox

**Description:**  
Connect the coordinator to the outbox so that `recorded` outcomes atomically write notifications.
Coordinator should not directly instantiate outbox; accept it as dependency injection.

**Acceptance Criteria:**
- `NotificationCoordinator` accepts optional `outbox: NotificationOutbox | None` in constructor
- When outbox is provided and outcome is `recorded`, atomically records transition and notification
- If outbox is `None`, coordinator still validates and maps but does not record
- Public API for retrieving or inspecting outbox state (e.g., read-only accessor)
- Type hints complete
- Docstring explains dependency injection and outbox contract

**Dependencies:** TASK-006, TASK-007

**Effort:** S (0.5–1 day)

---

### TASK-009: Define public API exports and integration boundary

**Description:**  
Determine which notification classes and functions are exported from `dreamguard.__init__` or remain internal to notifications module.
Document integration points for orchestration code to detect transitions and call coordinator.

**Acceptance Criteria:**
- Document decision: which classes are public (e.g., `SyntheticContactDestination`, `ClaimNotification`, `NotificationOutcome`, `NotificationCoordinator`, `NotificationOutbox`)?
- Add exports to `src/dreamguard/__init__.py` as decided
- Document in `src/dreamguard/__init__.py` and/or module docstrings that all data is synthetic
- No changes to existing `Claim`, `ClaimDecision`, `assess_claim`, `load_claims` exports
- Example integration pattern documented: "Caller detects status change, calls coordinator.notify(ClaimStatusChange)"
- Backward compatibility verified: existing tests for `assess_claim` and `load_claims` pass unchanged

**Dependencies:** TASK-001–008 (foundational decision after core implementation)

**Effort:** S (0.5–1 day)

---

### TASK-010: Write unit tests for SyntheticContactDestination and data models

**Description:**  
Create focused unit tests for immutability, type correctness, and instantiation of all four data models.

**Acceptance Criteria:**
- `tests/test_notifications.py` created
- Test class `TestSyntheticContactDestination` with:
  - `test_synthetic_contact_instantiation_with_valid_data`
  - `test_synthetic_contact_is_frozen` (verify immutability)
  - `test_synthetic_contact_with_synthetic_flag_true_and_false`
- Test class `TestClaimStatusChange` with instantiation and immutability tests
- Test class `TestClaimNotification` with instantiation and immutability tests
- Test class `TestNotificationOutcome` with instantiation and immutability tests
- All tests use synthetic test data
- Tests pass without errors
- Test names descriptive per project standards

**Dependencies:** TASK-001–003

**Effort:** S (0.5–1 day)

---

### TASK-011: Write unit tests for status mapping, templates, and contact validation

**Description:**  
Create focused unit tests for deterministic mapping, template rendering, and contact validation logic.

**Acceptance Criteria:**
- Test class `TestStatusMapping` with:
  - `test_map_pending_documents_to_client_pending_status`
  - `test_map_referred_to_client_referred_status`
  - `test_map_approved_to_client_approved_status`
  - `test_unknown_status_returns_unsupported_or_none`
- Test class `TestMessageTemplates` with:
  - `test_pending_template_includes_claim_reference_and_synthetic_marker`
  - `test_referred_template_includes_claim_reference_and_synthetic_marker`
  - `test_approved_template_includes_claim_reference_and_synthetic_marker`
  - Verify templates do not include amounts, documents, reasons, or raw destinations
- Test class `TestContactValidation` with:
  - `test_valid_synthetic_contact_returns_true`
  - `test_invalid_contact_with_is_synthetic_false_returns_false`
  - `test_empty_destination_value_returns_false`
  - `test_non_reserved_email_domain_rejected_if_enforced`
- All tests use synthetic data
- Tests pass without errors

**Dependencies:** TASK-004, TASK-005

**Effort:** M (1–2 days)

---

### TASK-012: Write unit tests for NotificationCoordinator orchestration logic

**Description:**  
Create focused unit tests for the coordinator's validation, deduplication, outcome code logic,
and integration with outbox.

**Acceptance Criteria:**
- Test class `TestNotificationCoordinator` with:
  - `test_recorded_outcome_for_complete_valid_transition` (pending, referred, approved)
  - `test_unchanged_status_suppresses_notification_when_previous_and_current_match`
  - `test_duplicate_transition_suppresses_notification_on_retry`
  - `test_invalid_contact_outcome_for_non_synthetic_destination`
  - `test_invalid_contact_outcome_for_empty_destination`
  - `test_invalid_transition_outcome_for_missing_claim_reference`
  - `test_invalid_transition_outcome_for_missing_transition_id`
  - `test_unsupported_status_outcome_for_unknown_status`
  - `test_unsupported_status_outcome_for_rejected_when_no_source_configured`
  - `test_validation_order_consistent_across_calls_with_multiple_defects`
- Coordinator with no outbox returns outcomes but does not record
- Coordinator with outbox atomically records on `recorded` outcome
- Tests verify no outbox writes for non-`recorded` outcomes
- All tests use synthetic data and fixtures
- Tests pass without errors
- Test names descriptive per project standards

**Dependencies:** TASK-006, TASK-007, TASK-008

**Effort:** M (1–2 days)

---

### TASK-013: Write unit tests for NotificationOutbox and deduplication

**Description:**  
Create focused unit tests for in-memory outbox storage, duplicate detection, and ordering.

**Acceptance Criteria:**
- Test class `TestNotificationOutbox` with:
  - `test_record_stores_notification_with_transition_id`
  - `test_duplicate_transition_id_raises_exception`
  - `test_get_notifications_returns_ordered_list`
  - `test_has_transition_returns_true_for_recorded_id`
  - `test_has_transition_returns_false_for_unrecorded_id`
  - `test_count_returns_number_of_recorded_notifications`
  - `test_outbox_is_deterministic_across_multiple_records`
- Docstring in tests notes that outbox is ephemeral (no persistence across instances)
- All tests use synthetic data
- Tests pass without errors

**Dependencies:** TASK-007

**Effort:** S (0.5–1 day)

---

### TASK-014: Write integration tests for end-to-end claim assessment → notification flow

**Description:**  
Create integration tests that demonstrate the complete flow: load claim, assess claim, detect transition,
notify, verify notification in outbox.

**Acceptance Criteria:**
- Test class `TestClaimAssessmentNotificationFlow` with:
  - `test_new_claim_pending_documents_generates_notification`
  - `test_reassessed_claim_to_approved_generates_different_transition_notification`
  - `test_reassessed_claim_with_unchanged_status_no_duplicate_notification`
  - `test_complete_flow_preserves_existing_assessment_behavior`
- Tests load synthetic claims, call `assess_claim`, construct `ClaimStatusChange`, call coordinator
- Verify that existing `test_claims.py` tests pass unchanged
- All tests use synthetic data
- Tests pass without errors
- Test names descriptive per project standards

**Dependencies:** TASK-001–013, requires existing assessment tests to pass

**Effort:** M (1–2 days)

---

### TASK-015: Update SERVICE.md with notification design and examples

**Description:**  
Add comprehensive documentation to `docs/SERVICE.md` describing the notification domain, status mappings,
outcome codes, examples of valid/invalid transitions, and guidance for operators.

**Acceptance Criteria:**
- New "Notifications" section in SERVICE.md covering:
  - Notification domain responsibility and separation from assessment
  - Status mapping table (internal → client-facing)
  - Outcome codes table with meanings and examples
  - Contact validation rules and synthetic-only requirement
  - Example transition flow with synthetic data
  - Deterministic deduplication guarantees
  - In-memory outbox caveats and ephemeral nature
  - Integration pattern: how to call coordinator
- No existing SERVICE.md sections removed or renamed
- Examples use only synthetic values (`.invalid` domains, `POL-*` references)
- Tone matches existing documentation
- Markdown formatting correct

**Dependencies:** TASK-001–014 (after implementation stable)

**Effort:** S (0.5–1 day)

---

### TASK-016: Add module docstrings to notifications.py and update __init__.py docstring

**Description:**  
Add or update module-level docstrings in `src/dreamguard/notifications.py` and ensure `src/dreamguard/__init__.py`
includes note that all data is synthetic per project standards.

**Acceptance Criteria:**
- `src/dreamguard/notifications.py` has module docstring explaining:
  - Notification orchestration separate from assessment
  - Deterministic synthetic notification delivery
  - All records are synthetic for training
- `src/dreamguard/__init__.py` updated to note synthetic-only data policy if exports added
- Docstrings reference project standards and explain no real data
- Tone matches existing docstrings
- Markdown code blocks or examples use synthetic data

**Dependencies:** TASK-001–014

**Effort:** XS (< 0.5 day)

---

### TASK-017: Run full test suite and verify backward compatibility

**Description:**  
Execute entire test suite including existing `tests/test_claims.py` and `tests/test_app.py` to verify
no regressions. Confirm all assessment and intake behavior is unchanged.

**Acceptance Criteria:**
- Command: `python -m unittest discover -s tests -v` passes
- All existing tests pass without modification
- New notification tests (`tests/test_notifications.py`) pass
- Assessment (`test_claims.py`) tests unchanged and passing
- App tests (`test_app.py`) unchanged and passing
- Test coverage for new code is ≥ 90%
- No warnings or deprecations introduced

**Dependencies:** TASK-001–016

**Effort:** S (0.5–1 day)

---

## Task Dependencies and DAG

```
TASK-001: SyntheticContactDestination
  ↓
TASK-002: ClaimStatusChange, ClaimNotification
  ├─ TASK-003: NotificationOutcome
  ├─ TASK-004: Status mapping and templates
  ├─ TASK-005: Contact validation
  └─ TASK-006: NotificationCoordinator
      └─ TASK-007: NotificationOutbox
          └─ TASK-008: Coordinator + Outbox integration
              └─ TASK-009: Public API exports
                  └─ TASK-010: Unit tests for data models
                      └─ TASK-011: Unit tests for status/templates/validation
                          └─ TASK-012: Unit tests for coordinator
                              └─ TASK-013: Unit tests for outbox
                                  └─ TASK-014: Integration tests
                                      └─ TASK-015: Update SERVICE.md
                                          └─ TASK-016: Module docstrings
                                              └─ TASK-017: Full test suite verification
```

**Critical path:** TASK-001 → TASK-002 → TASK-003 → TASK-006 → TASK-007 → TASK-008 → TASK-012 → TASK-014 → TASK-017

**Parallelizable:** TASK-004, TASK-005 can proceed in parallel after TASK-001–003 complete.

---

## Effort Estimate

| Task | Effort | Notes |
|------|--------|-------|
| TASK-001 | XS | Trivial immutable class |
| TASK-002 | S | Two immutable dataclasses |
| TASK-003 | S | Single immutable dataclass |
| TASK-004 | S | Templates and mapping |
| TASK-005 | S | Contact validation |
| TASK-006 | M | Coordinator orchestration logic |
| TASK-007 | S | In-memory storage |
| TASK-008 | S | Dependency injection |
| TASK-009 | S | API boundary decision |
| TASK-010 | S | Data model tests |
| TASK-011 | M | Templates and validation tests |
| TASK-012 | M | Coordinator orchestration tests |
| TASK-013 | S | Outbox tests |
| TASK-014 | M | Integration tests |
| TASK-015 | S | Documentation update |
| TASK-016 | XS | Module docstrings |
| TASK-017 | S | Test suite execution |
| **Total** | **8–12 days** | **Recommended 2–3 developers** |

**Timeline breakdown:**
- **Days 1–2:** Data models (TASK-001–003) + parallel templates and validation (TASK-004–005)
- **Days 2–3:** Coordinator and outbox (TASK-006–008)
- **Day 3:** Public API boundary (TASK-009)
- **Days 4–5:** Unit tests (TASK-010–013)
- **Day 6:** Integration tests (TASK-014)
- **Days 6–7:** Documentation and final verification (TASK-015–017)

---

## Resource Allocation

**Recommended team composition:**

- **1 Domain expert** (1.5–2 days): Leads TASK-004–006 (status mapping, contact validation, coordinator logic). Pairs with domain knowledge of claim assessment and notification invariants.
- **1 Test engineer** (2.5–3 days): Leads TASK-010–014 (comprehensive unit and integration tests). Ensures fixtures, synthetic data, and test scenarios are complete.
- **1 Full-stack developer** (2–2.5 days): Handles TASK-001–003, TASK-007–009, TASK-016–017 (data models, storage, API, verification). Can also support tests.

**Key skills:**
- Python 3.10+ (type hints, dataclasses, frozen semantics)
- Immutable data modeling
- Deterministic testing with synthetic fixtures
- Project standards (decimal for money, PEP 8 naming, module docstrings)

---

## Success Criteria

- All 17 tasks completed in documented order or as parallelized
- All tests pass (`python -m unittest discover -s tests -v`)
- Test coverage for notification module ≥ 90%
- Zero regressions in existing assessment or intake behavior
- All data models and messaging use synthetic values only
- Docstrings and comments meet project standards
- SERVICE.md reflects implemented design and feature behavior
