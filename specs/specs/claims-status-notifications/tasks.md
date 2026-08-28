# Claims-Status Notifications — Task Breakdown

**Status:** Phase 3 — Tasks + Summary  
**Date:** 2026-08-28  
**Feature:** Claims-Status Notifications System

---

## Overview

This document breaks the approved design into granular, actionable development tasks organized by implementation category. Tasks are sequenced by dependency and logical workflow.

**Effort Estimate:** 30–40 story points across all categories  
**Timeline:** 2–3 weeks with standard team capacity

---

## Category 1: Data Models & Core Logic (Foundation)

### Task 1.1: Create ContactDetails Immutable Dataclass

**Description:**  
Implement the `ContactDetails` immutable dataclass with validation in `__post_init__`. Validate that `name`, `email`, and `phone` are non-empty and that `email` contains an "@" character. Ensure the dataclass is frozen to prevent post-creation modification.

**Complexity:** Low  
**Dependencies:** None  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `ContactDetails` dataclass with `frozen=True`
- ✅ `name`, `email`, `phone` fields are `str` type
- ✅ `__post_init__` validates non-empty and email format
- ✅ `ValueError` raised with clear message on invalid input
- ✅ Can instantiate with synthetic data: `ContactDetails(name="Jane Doe", email="jane.doe@example.com", phone="+1-555-0123")`
- ✅ Unit tests pass (see Task 4.1)

---

### Task 1.2: Create NotificationEvent Immutable Dataclass

**Description:**  
Implement the `NotificationEvent` immutable dataclass that captures a single notification trigger event. Include `claim_id`, `claim_type`, `status`, `contact_details` (ContactDetails), `triggered_at` (datetime), `approved_amount` (Decimal or None), and `reasons` (tuple of str). Ensure immutability and type hints.

**Complexity:** Low  
**Dependencies:** Task 1.1 (ContactDetails must exist)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `NotificationEvent` dataclass with `frozen=True`
- ✅ All fields have explicit type hints (e.g., `contact_details: ContactDetails`, `approved_amount: Decimal | None`)
- ✅ `triggered_at` defaults to `datetime.now()`
- ✅ `approved_amount` is `Decimal` (never float)
- ✅ `reasons` is immutable tuple
- ✅ Can instantiate with synthetic data
- ✅ Unit tests pass (see Task 4.2)

---

### Task 1.3: Add ContactDetails Field to Claim Model (Backward Compatible)

**Description:**  
Extend the existing `Claim` dataclass in `src/dreamguard/claims.py` to include an optional `contact_details: ContactDetails | None = None` field. Ensure backward compatibility: existing code that creates `Claim` instances without this field continues to work. Update `load_claims()` in `intake.py` to extract contact details from JSON if present.

**Complexity:** Low  
**Dependencies:** Task 1.1 (ContactDetails must exist)  
**Owner:** TBD  
**File Location:** `src/dreamguard/claims.py`, `src/dreamguard/intake.py`

**Success Criteria:**
- ✅ `Claim` dataclass has optional `contact_details: ContactDetails | None = None`
- ✅ Existing tests still pass (no breaking changes)
- ✅ `load_claims()` extracts `contact_details` from JSON if present (keys: `name`, `email`, `phone`)
- ✅ Backward-compatible: JSON with no contact details still loads as `contact_details=None`
- ✅ Integration tests verify end-to-end JSON loading (see Task 4.6)

---

### Task 1.4: Implement NotificationLog Append and Query Methods

**Description:**  
Create a `NotificationLog` class that maintains an immutable, append-only log of `NotificationEvent` instances. Implement `append(event: NotificationEvent) -> None` to add events and `list_events() -> tuple[NotificationEvent, ...]` to retrieve all logged events. Use a tuple internally to prevent mutation. Provide optional filtering by claim_id or status.

**Complexity:** Medium  
**Dependencies:** Task 1.2 (NotificationEvent must exist)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `NotificationLog` class with immutable internal storage (tuple)
- ✅ `append(event: NotificationEvent) -> None` method adds events
- ✅ `list_events() -> tuple[NotificationEvent, ...]` returns all logged events
- ✅ Optional `filter_by_claim_id(claim_id: str) -> tuple[NotificationEvent, ...]` method
- ✅ Optional `filter_by_status(status: str) -> tuple[NotificationEvent, ...]` method
- ✅ Thread-safe append (basic locking if needed for demo purposes)
- ✅ Unit tests for append and retrieval (see Task 4.7)

---

## Category 2: Notification System (Core Feature)

### Task 2.1: Create NotificationChannel Base Strategy Class

**Description:**  
Define an abstract base class `NotificationChannel` with a `send(event: NotificationEvent) -> bool` method. This class serves as a strategy interface for different notification delivery mechanisms (email, SMS, etc.). Implement it as an ABC with `abstractmethod`.

**Complexity:** Low  
**Dependencies:** Task 1.2 (NotificationEvent must exist)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `NotificationChannel` is an `ABC` with `abstractmethod`
- ✅ `send(event: NotificationEvent) -> bool` is the abstract method
- ✅ Return value indicates delivery success (True for mock channels, for now)
- ✅ Clear docstring explaining the contract
- ✅ Type hints on all parameters and return values

---

### Task 2.2: Implement MockEmailChannel Strategy

**Description:**  
Implement a `MockEmailChannel` subclass of `NotificationChannel` that logs emails to a list or tuple without actually sending. For training purposes, this channel simply records the notification in memory. Include mock logic to extract email from `contact_details` and format a simple notification message.

**Complexity:** Low  
**Dependencies:** Task 2.1 (NotificationChannel base class)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `MockEmailChannel` inherits from `NotificationChannel`
- ✅ `send(event: NotificationEvent) -> bool` returns True (simulated success)
- ✅ Formats a message like: "Email to {contact_details.email}: Claim {claim_id} status is {status}"
- ✅ Can be called multiple times without side-effects beyond internal state
- ✅ Unit tests pass (see Task 4.4)

---

### Task 2.3: Implement MockSMSChannel Strategy

**Description:**  
Implement a `MockSMSChannel` subclass of `NotificationChannel` that logs SMS notifications without actually sending. Similar to `MockEmailChannel`, this channel records the notification in memory and formats a message using the phone number from `contact_details`.

**Complexity:** Low  
**Dependencies:** Task 2.1 (NotificationChannel base class)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `MockSMSChannel` inherits from `NotificationChannel`
- ✅ `send(event: NotificationEvent) -> bool` returns True
- ✅ Formats a message like: "SMS to {contact_details.phone}: Claim {claim_id} status is {status}"
- ✅ No actual SMS delivery (training mock)
- ✅ Unit tests pass (see Task 4.5)

---

### Task 2.4: Create NotificationDispatcher with Status-to-Channel Mapping

**Description:**  
Implement a `NotificationDispatcher` class that routes `NotificationEvent` instances to appropriate `NotificationChannel` instances based on claim status. Use a data-driven mapping (dictionary or configuration object) that defines which channels handle which statuses:

```python
{
    "approved": [MockEmailChannel()],
    "referred": [MockEmailChannel()],
    "pending_documents": [MockEmailChannel()],
}
```

The dispatcher's `dispatch(event: NotificationEvent) -> None` method looks up the status, retrieves configured channels, and calls `send()` on each.

**Complexity:** Medium  
**Dependencies:** Task 2.1 (NotificationChannel), Task 2.2 (MockEmailChannel), Task 2.3 (MockSMSChannel)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ `NotificationDispatcher` class with configurable status-to-channel mapping
- ✅ `dispatch(event: NotificationEvent) -> None` method routes to correct channels
- ✅ Default mapping includes "referred", "pending_documents", "approved"
- ✅ Graceful handling of unknown statuses (log warning or skip)
- ✅ Type hints on all methods
- ✅ Integration tests verify correct channel routing (see Task 4.6)

---

## Category 3: Integration with assess_claim() (Workflow)

### Task 3.1: Create handle_claim_assessment() Orchestrator Function

**Description:**  
Implement a top-level function `handle_claim_assessment(claim: Claim, dispatcher: NotificationDispatcher, notification_log: NotificationLog) -> ClaimDecision` that orchestrates the full workflow:

1. Call the existing `assess_claim(claim)` to get a decision (no modification to `assess_claim()` itself)
2. If `claim.contact_details` is not None and the decision status is notifiable, create a `NotificationEvent`
3. Add the event to `notification_log`
4. Call `dispatcher.dispatch(event)` to send notifications
5. Return the original `ClaimDecision` unchanged

This ensures `assess_claim()` remains pure and side-effect-free.

**Complexity:** Medium  
**Dependencies:** Task 1.2 (NotificationEvent), Task 1.4 (NotificationLog), Task 2.4 (NotificationDispatcher), existing `assess_claim()` function  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py` or `src/dreamguard/__init__.py`

**Success Criteria:**
- ✅ `handle_claim_assessment()` calls `assess_claim()` without modifying it
- ✅ Creates `NotificationEvent` with all required fields (claim_id, status, contact_details, triggered_at, approved_amount, reasons)
- ✅ Adds event to `notification_log` via `append()`
- ✅ Calls `dispatcher.dispatch()` with the event
- ✅ Returns original `ClaimDecision` unchanged
- ✅ Handles None `contact_details` gracefully (no notification if missing)
- ✅ Full type hints on function signature
- ✅ Integration tests pass (see Task 4.6)

---

### Task 3.2: Ensure Backward Compatibility with Existing API

**Description:**  
Verify that the new notification system does not break existing code. Run all existing tests (`tests/test_claims.py`, `tests/test_app.py`) to ensure they still pass. The original `assess_claim()` function must remain unchanged in signature and behavior. Existing callers should not be forced to use the new `handle_claim_assessment()` function.

**Complexity:** Low  
**Dependencies:** All previous tasks  
**Owner:** TBD  
**File Location:** (Verification task, no new code)

**Success Criteria:**
- ✅ All existing unit tests pass without modification
- ✅ Existing integration tests pass
- ✅ `assess_claim()` signature unchanged
- ✅ No breaking changes to public API
- ✅ `load_claims()` works with JSON that has no contact details
- ✅ Demo or app.py runs without errors

---

## Category 4: Testing (Quality)

### Task 4.1: Unit Tests for ContactDetails Validation

**Description:**  
Write unit tests for the `ContactDetails` class covering valid instantiation and validation error cases.

**Complexity:** Low  
**Dependencies:** Task 1.1 (ContactDetails implementation)  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test valid instantiation with synthetic data
- ✅ Test ValueError on empty `name`
- ✅ Test ValueError on empty `email`
- ✅ Test ValueError on invalid email (missing "@")
- ✅ Test ValueError on empty `phone`
- ✅ Test that frozen dataclass prevents attribute assignment after creation
- ✅ Use synthetic data only (no real names, emails, or phone numbers)
- ✅ All tests pass

---

### Task 4.2: Unit Tests for NotificationEvent Creation

**Description:**  
Write unit tests for `NotificationEvent` instantiation, field validation, and immutability.

**Complexity:** Low  
**Dependencies:** Task 1.2 (NotificationEvent implementation)  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test valid instantiation with all required fields
- ✅ Test `triggered_at` defaults to current datetime
- ✅ Test `approved_amount` is Decimal (not float)
- ✅ Test `reasons` is immutable tuple
- ✅ Test that frozen dataclass prevents attribute assignment
- ✅ Test with synthetic claim data
- ✅ All tests pass

---

### Task 4.3: Unit Tests for NotificationChannel and Mock Implementations

**Description:**  
Write unit tests for `NotificationChannel` base class and both mock channel implementations (`MockEmailChannel`, `MockSMSChannel`).

**Complexity:** Low  
**Dependencies:** Task 2.1, Task 2.2, Task 2.3  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test that `MockEmailChannel.send()` returns True
- ✅ Test that `MockEmailChannel` formats message with email address
- ✅ Test that `MockSMSChannel.send()` returns True
- ✅ Test that `MockSMSChannel` formats message with phone number
- ✅ Test with synthetic contact details
- ✅ All tests pass

---

### Task 4.4: Unit Tests for NotificationDispatcher

**Description:**  
Write unit tests for the `NotificationDispatcher` class, verifying that notifications are routed to the correct channels based on status.

**Complexity:** Low  
**Dependencies:** Task 2.4 (NotificationDispatcher implementation)  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test dispatch of "approved" status routes to email channel
- ✅ Test dispatch of "referred" status routes to email channel
- ✅ Test dispatch of "pending_documents" status routes to email channel
- ✅ Test unknown status is handled gracefully
- ✅ Test with synthetic claim data and contact details
- ✅ All tests pass

---

### Task 4.5: Unit Tests for NotificationLog

**Description:**  
Write unit tests for the `NotificationLog` class, verifying append, retrieval, and filtering functionality.

**Complexity:** Low  
**Dependencies:** Task 1.4 (NotificationLog implementation)  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test `append()` adds a single event to log
- ✅ Test `list_events()` returns all appended events in order
- ✅ Test `filter_by_claim_id()` returns events for specific claim
- ✅ Test `filter_by_status()` returns events with specific status
- ✅ Test that log maintains immutable tuple internally
- ✅ Test with multiple synthetic events
- ✅ All tests pass

---

### Task 4.6: Integration Tests for handle_claim_assessment()

**Description:**  
Write integration tests that verify the full workflow: claim assessment, notification event creation, logging, and dispatcher routing.

**Complexity:** Medium  
**Dependencies:** All previous tasks (1.x, 2.x, 3.1)  
**Owner:** TBD  
**File Location:** `tests/test_notifications.py`

**Success Criteria:**
- ✅ Test "approved" status creates notification event and logs it
- ✅ Test "referred" status creates notification event and logs it
- ✅ Test "pending_documents" status creates notification event and logs it
- ✅ Test that original `ClaimDecision` is returned unchanged
- ✅ Test with claim that has `contact_details` set
- ✅ Test with claim that has `contact_details = None` (no notification sent)
- ✅ Test notification log contains expected events after workflow completes
- ✅ Use synthetic data only
- ✅ All tests pass

---

### Task 4.7: Backward Compatibility Regression Tests

**Description:**  
Run all existing tests to ensure no breaking changes. Verify that existing functionality continues to work when the notification system is added.

**Complexity:** Low  
**Dependencies:** Task 3.2 (backward compatibility verification)  
**Owner:** TBD  
**File Location:** (Verification task)

**Success Criteria:**
- ✅ Run `python -m unittest discover -s tests -v` and all tests pass
- ✅ Existing `test_claims.py` passes without modification
- ✅ Existing `test_app.py` passes without modification
- ✅ No regression in existing functionality
- ✅ Score script (`scripts/score.py`) runs successfully

---

## Category 5: Documentation (Completeness)

### Task 5.1: Add Google-Style Docstrings to All Public Functions

**Description:**  
Write or update docstrings for all public functions and classes introduced by this feature:
- `ContactDetails`
- `NotificationEvent`
- `NotificationChannel`
- `MockEmailChannel`
- `MockSMSChannel`
- `NotificationDispatcher`
- `NotificationLog`
- `handle_claim_assessment()`

Use Google-style format with Args, Returns, Raises, and Examples sections.

**Complexity:** Low  
**Dependencies:** All implementation tasks (1.x, 2.x, 3.x)  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`, `src/dreamguard/__init__.py`

**Success Criteria:**
- ✅ All public classes and functions have module-level docstrings
- ✅ Each docstring includes Args, Returns, Raises (where applicable)
- ✅ Examples use synthetic data and demonstrate typical usage
- ✅ Examples are valid Python and follow DreamGuard style
- ✅ No typos or formatting errors

---

### Task 5.2: Update SERVICE.md with Notification Feature Documentation

**Description:**  
Update the `docs/SERVICE.md` file to document the new notification feature. Add sections explaining:
- What the notification system does
- How it integrates with `assess_claim()`
- Example JSON input with contact details
- Example notification events
- How to use `handle_claim_assessment()` and `NotificationLog`

**Complexity:** Low  
**Dependencies:** All implementation tasks  
**Owner:** TBD  
**File Location:** `docs/SERVICE.md`

**Success Criteria:**
- ✅ New "Notifications" section added to SERVICE.md
- ✅ Describes the three decision statuses and corresponding notifications
- ✅ Includes example JSON with contact details
- ✅ Shows example of using `handle_claim_assessment()`
- ✅ Explains NotificationLog usage
- ✅ Consistent with existing documentation style
- ✅ All synthetic data in examples

---

### Task 5.3: Add Inline Comments for Complex Logic

**Description:**  
Review implementation code (especially `handle_claim_assessment()`, `NotificationDispatcher.dispatch()`, and `NotificationEvent` creation) and add inline comments explaining complex logic, decisions, and gotchas.

**Complexity:** Low  
**Dependencies:** All implementation tasks  
**Owner:** TBD  
**File Location:** `src/dreamguard/notifications.py`

**Success Criteria:**
- ✅ Complex branching logic has explanatory comments
- ✅ Rationale for design choices is documented
- ✅ Edge cases (e.g., `contact_details = None`) are explained
- ✅ Comments follow Python conventions (single # for inline, """ for blocks)
- ✅ Comments are concise and add value without being redundant

---

## Category 6: Public API (Interface)

### Task 6.1: Add Exports to __init__.py

**Description:**  
Update `src/dreamguard/__init__.py` to export the new public classes and functions:
- `ContactDetails`
- `NotificationEvent`
- `NotificationLog`
- `NotificationChannel`
- `MockEmailChannel`
- `MockSMSChannel`
- `NotificationDispatcher`
- `handle_claim_assessment()`

Ensure all exports are included in `__all__` and maintain backward compatibility (do not remove existing exports).

**Complexity:** Low  
**Dependencies:** All implementation tasks (1.x, 2.x, 3.x)  
**Owner:** TBD  
**File Location:** `src/dreamguard/__init__.py`

**Success Criteria:**
- ✅ All new classes and functions are exported
- ✅ `__all__` list is updated
- ✅ Existing exports remain unchanged (backward compatible)
- ✅ All exports have type hints in their definitions
- ✅ Imports work from `dreamguard` package: `from dreamguard import ContactDetails, NotificationEvent`
- ✅ Documentation/type hints are accessible via help()

---

### Task 6.2: Verify Type Hints on All Exports

**Description:**  
Perform a final audit of all public API functions and classes to ensure they have complete type hints. Use `mypy` or Pylance to check for missing annotations.

**Complexity:** Low  
**Dependencies:** All implementation tasks  
**Owner:** TBD  
**File Location:** (Verification task)

**Success Criteria:**
- ✅ All public functions have return type hints
- ✅ All public function parameters have type hints
- ✅ All dataclass fields have type hints
- ✅ Type checker (Pylance) shows no missing type errors
- ✅ `Decimal` used for monetary amounts (never `float`)

---

## Task Sequencing and Dependencies

### Phase 1: Data Models (Tasks 1.1–1.4)
- Start with `ContactDetails` (1.1)
- Then `NotificationEvent` (1.2)
- Add `contact_details` field to `Claim` (1.3)
- Implement `NotificationLog` (1.4)

### Phase 2: Notification Channels (Tasks 2.1–2.4)
- Define `NotificationChannel` base class (2.1)
- Implement `MockEmailChannel` (2.2)
- Implement `MockSMSChannel` (2.3)
- Create `NotificationDispatcher` (2.4)

### Phase 3: Integration (Tasks 3.1–3.2)
- Implement `handle_claim_assessment()` orchestrator (3.1)
- Verify backward compatibility (3.2)

### Phase 4: Testing (Tasks 4.1–4.7)
- Begin writing tests in parallel with implementation
- Unit tests for individual components (4.1–4.5)
- Integration tests (4.6)
- Regression tests (4.7)

### Phase 5: Documentation & Polish (Tasks 5.1–6.2)
- Add docstrings (5.1)
- Update SERVICE.md (5.2)
- Add inline comments (5.3)
- Export to public API (6.1)
- Verify type hints (6.2)

---

## Summary of Success Metrics

| Metric | Target |
|--------|--------|
| Code Coverage | ≥ 90% for new notification code |
| Test Count | ≥ 25 unit/integration tests |
| Type Hints | 100% on public API |
| Backward Compatibility | All existing tests pass |
| Documentation | All public functions have docstrings + examples |
| Code Style | PEP 8 compliant, no linter errors |
| Synthetic Data | 100% of test data is fictional |

