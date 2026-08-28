# Claims Status Notifications — Phase 3: Tasks

**Status:** Pending approval

---

## Setup

1. Ensure `specs/claims-notifications/` directory exists (already created)
2. Backup current `data/sample_claims.json` (will be updated with contact fields)
3. Review [design.md](design.md) before starting implementation

---

## Tasks

### Task 1: Write Implementation Decision Specification

**Files:** `specs/claims-notifications/implementation-decisions.md` (new file)

**Description:**
Before any code implementation begins, Task 1 must produce a written specification document that finalizes the 4 critical design decisions identified in the specification review. This is a prerequisite for Tasks 2-7 and unblocks the critical path. The document must provide concrete specifications with examples, not just guidance.

**Critical blockers to resolve and document:**

#### 1. Contact Validator Algorithm

**Specification task:** Define the deterministic validator for contact fields.

**Must include:**
- Algorithm or rule set (pattern matching? callable? hardcoded valid examples?)
- Example of **valid** contact: e.g., `client-1001@example.invalid`
- Example of **invalid** contact that should be rejected: e.g., `user@gmail.com`
- Whether `.invalid` is required or can other fictional domains be accepted (`.test`, `.synthetic`, etc.)
- Behavior when contact is empty, malformed, or real-world-looking (e.g., `john@company.com`)
- Return type: accept/reject, or return error code (e.g., `invalid_contact`)?

**Example specification:**
```
Validator: Email-shaped contact with .invalid domain or reserved test domain
Accepts: client-\d+@example.invalid, .*@test.invalid, .*@.synthetic
Rejects: Contains real domains (gmail, outlook, .com, .co.za); empty; no @; etc.
Invalid contact outcome: recorded as `invalid_contact` code, no notification written
```

#### 2. Transition ID Format and Generation

**Specification task:** Define how transitions are uniquely identified.

**Must include:**
- Format: UUID, hash, opaque string, or caller-supplied?
- Generation: who generates it? (orchestration caller? workflow system? coordinator?)
- Uniqueness: guaranteed across process restarts? within single process lifetime only?
- Immutability: does same transition always get same ID?
- Examples: what does a real transition ID look like?
- How duplicate detection works: string equality? UUID comparison? hash collision handling?

**Example specification:**
```
Format: UUID v4 (RFC 4122), supplied by orchestration caller
Generation: Caller responsibility; must be stable and unique per transition
Uniqueness: Stable across restarts; same transition = same UUID always
Immutability: Yes; immutable once assigned
Duplicate detection: In-memory registry of seen transition_ids; string equality check
Example: 123e4567-e89b-12d3-a456-426614174000
```

#### 3. Outbox API Signatures

**Specification task:** Define the public interface for the in-memory outbox.

**Must include:**
- Method/property names (e.g., `records`, `get_all()`, `by_transition_id()`)
- Return types (tuple? list? custom iterator? frozen?)
- Immutability guarantees (can returned data be mutated? what about internal state?)
- Query interface: can you look up by transition_id? by claim_reference?
- Count method for tests
- Example usage (how does code inspect recorded notifications?)

**Example specification:**
```
outbox.records: property returning tuple[Notification, ...] (immutable)
outbox.count(): int — number of recorded notifications
outbox.get_by_transition_id(tid: str) → tuple[Notification, ...] | None
outbox.get_by_claim_reference(ref: str) → tuple[Notification, ...]
All return types are frozen/immutable; internal state cannot be mutated
Usage: for notif in outbox.records: ...
```

#### 4. Message Template Strings

**Specification task:** Define the exact template text for each decision status.

**Must include:**
- Exact subject line (for email) for each status
- Exact body/message text for each status
- Placeholders (how are claim_reference, amount, missing_docs substituted?)
- Location of synthetic/simulated language marker (in every message? subject? footer?)
- Sender/signature information (if any)
- Examples of rendered messages with actual placeholders filled in

**Example specification:**
```
STATUS: approved
Email Subject: "Your Claim {claim_reference} Has Been Approved (Simulated)"
Email Body:
  "Good news! Your synthetic claim {claim_reference} has been approved. 
   This is a simulated notification. Expected processing time: 5-7 business days."

SMS:
  "DreamGuard: Synthetic claim {claim_reference} approved. This is a simulation. Check dashboard for details."

STATUS: pending_documents
Email Subject: "Action Required: Documents Needed for Claim {claim_reference} (Simulated)"
Email Body:
  "We need the following documents for your synthetic claim {claim_reference}:
   {missing_documents_list}
   Please upload them to your account. This is a simulated notification."

SMS:
  "DreamGuard: Claim {claim_reference} needs {doc_count} docs (simulated). Upload now."

[Define all 3-4 statuses with concrete text]
```

#### 5. Claim Reference Format

**Specification task:** Define the format of claim references in notifications.

**Must include:**
- What is a claim reference? (policy number? claim ID? synthetic identifier?)
- Format/pattern (e.g., `PREM-001`, `CLM-12345`, policy_number, UUID?)
- Who supplies it? (from `Claim` object? from orchestration caller?)
- Must it be unique? synthetic? real-world-free?
- Example values: what do real claim references look like?

**Example specification:**
```
Claim reference: Policy number from Claim.policy_number
Format: Alphanumeric, synthetic-only (e.g., SYN-1001, TEST-CLI-9999)
Source: Claim.policy_number passed through to notification
Requirements: No real policy formats; clearly fictional
Examples: SYN-1001, TEST-CLAIM-99999, SYNTHETIC-456
```

#### 6. Simulated/Synthetic Language Requirements

**Specification task:** Define where and how "this is simulated/synthetic" language appears.

**Must include:**
- Must it appear in every message, email subject, or footer?
- Exact wording: "simulated," "synthetic," "test," "fictional"?
- Frequency: every message or only first notification?
- Visibility: must it be prominent or can it be in footer?

**Example specification:**
```
Requirement: Every notification must clearly mark itself as synthetic/simulated
Placement: Either in subject line (email) or first sentence of body
Wording: "This is a simulated notification" or "Your synthetic claim"
Frequency: Every message (not just first)
Example: Subject line includes "(Simulated)" or body starts with "Your synthetic claim..."
```

#### 7. Operator Response Guidance for Outcome Codes

**Specification task:** Define what operators should do when they see each outcome.

**Must include:**
- Each outcome code: `recorded`, `unchanged_status`, `duplicate_transition`, `invalid_contact`, `invalid_transition`, `unsupported_status`
- For each: "is this expected?" "what action?"
- Severity: INFO, WARNING, ERROR?
- Logging level and redaction rules

**Example specification:**
```
recorded:              Expected success; INFO level; safe to ignore
unchanged_status:      Expected when status hasn't changed; INFO level; no action
duplicate_transition:  Expected retry; INFO level; safe to ignore
invalid_contact:       Needs investigation; WARNING level; operator reviews claim
invalid_transition:    Needs investigation; WARNING level; operator reviews data
unsupported_status:    Should not occur in normal workflow; ERROR level; investigate

Redaction: Never log raw destination or message body; log only transition_id, outcome, status
```

**Requirements:**
- Create `specs/claims-notifications/implementation-decisions.md` with all 7 specifications above
- Each specification must include concrete examples, not abstract guidance
- Specifications must be deterministic (same input = same behavior always)
- All synthetic data must use reserved/fictional values (.invalid, SYN-*, TEST-*, etc.)
- Format: readable Markdown with code blocks for examples and algorithm specifications

**Acceptance criteria:**
- `implementation-decisions.md` created with all 7 specifications
- Contact validator algorithm is specified with accept/reject examples
- Transition ID format, generation, and uniqueness are defined
- Outbox API has concrete method signatures with return types
- Message templates are provided in full for all statuses with placeholders
- Claim reference format is specified
- Simulated/synthetic language requirements are explicit and checkable
- Operator guidance for each outcome code is defined
- Document can be used as reference by Tasks 2-7 without ambiguity
- All specifications are deterministic (testable, reproducible)

**Dependencies:** None — this task must complete before Tasks 2-7 begin

**Note:** Task 1 is the critical path blocker. It produces written specifications that unblock Tasks 2-7. Implementation tasks should not proceed until Task 1 output is reviewed and approved.

---

### Task 2: Extend Claim dataclass with contact fields
**Files:** `src/dreamguard/claims.py`

**Description:**
Add email and phone fields to the Claim dataclass to carry synthetic contact information. Update the docstring to document these new fields and note that all contact details are synthetic.

**Requirements:**
- Add `email: str` field
- Add `phone: str` field
- Update the class docstring to describe the new fields
- Mark as frozen (maintain immutability)
- Add type hints for new fields
- Include synthetic data guidance in docstring

**Acceptance criteria:**
- Claim dataclass has email and phone attributes
- Field types are correctly annotated
- Docstring updated and mentions synthetic data
- Existing tests still pass (Claim remains frozen)

**Dependencies:** Task 1

---

### Task 3: Create Notification dataclass and notify_claim_decision() function
**Files:** `src/dreamguard/notifications.py` (new file)

**Description:**
Create a new module with the Notification dataclass and the core notify_claim_decision() function that generates email and SMS notifications based on claim decision status. Use the message templates and contact validator defined in Task 1's implementation-decisions.md.

**Requirements:**
- Create frozen Notification dataclass with fields: policy_number, channel, recipient, subject, message, decision_status
- Implement notify_claim_decision(claim, decision) function
- Generate two notifications (email + SMS) per claim
- Use decision-status-specific message templates from Task 1 specification
- Apply contact validator from Task 1 specification
- Return tuple of Notification objects
- Add comprehensive docstrings with type hints
- Include synthetic data note in module docstring

**Acceptance criteria:**
- notifications.py created with Notification and notify_claim_decision()
- Message templates match exactly those specified in Task 1
- Contact validator matches Task 1 specification
- Approved decisions generate proper messages
- Pending_documents decisions list missing docs
- Referred decisions include waiting period info
- Both email and SMS generated for each decision
- All code is fully type-hinted and documented
- Notifications are frozen dataclasses

**Dependencies:** Task 1 (must read implementation-decisions.md)

---

### Task 4: Update intake.py to load contact details from JSON
**Files:** `src/dreamguard/intake.py`

**Description:**
Update the load_claims() function to parse email and phone fields from JSON claim records and pass them to the Claim constructor.

**Requirements:**
- Extend load_claims() to read "email" and "phone" from JSON records
- Pass email and phone to Claim constructor
- Maintain backward compatibility (handle records without contact fields gracefully if needed)
- Update function docstring if necessary

**Acceptance criteria:**
- load_claims() parses email and phone from JSON
- Returns Claim objects with all fields populated
- Handles both old format (no contacts) and new format

**Dependencies:** Task 2 (Claim must have email/phone fields)

---

### Task 5: Update sample_claims.json with synthetic contact details
**Files:** `data/sample_claims.json`

**Description:**
Add synthetic (fictional) email and phone contact details to the sample claims data. Use completely fictional email domains and phone numbers based on the format specified in Task 1.

**Requirements:**
- Add email field to each claim matching Task 1 contact validator specification
- Add phone field to each claim matching Task 1 specification
- Ensure all contacts are clearly fictional
- Maintain existing fields (policy_number, claim_type, amount, months_active, documents)

**Acceptance criteria:**
- All sample claims have email and phone fields
- Emails match Task 1 validator specification
- Phones match Task 1 specification
- JSON is valid and parseable

**Dependencies:** Task 1 (must read contact format specifications)

---

### Task 6: Update public API exports
**Files:** `src/dreamguard/__init__.py`

**Description:**
Export Notification class and notify_claim_decision function from the dreamguard package so they're available to users.

**Requirements:**
- Import Notification from notifications module
- Import notify_claim_decision from notifications module
- Add both to __all__ list
- Maintain existing exports (Claim, ClaimDecision, assess_claim, load_claims)

**Acceptance criteria:**
- __all__ includes new exports
- Can import: `from dreamguard import Notification, notify_claim_decision`
- Existing API still accessible

**Dependencies:** Task 3 (notifications.py must exist)

---

### Task 7: Create comprehensive unit tests
**Files:** `tests/test_notifications.py` (new file)

**Description:**
Create a full test suite for the notifications module covering all decision types and notification generation scenarios.

**Requirements:**
- Test class: TestNotifyClaimDecision
- Test for approved claim → generates email + SMS with approval messaging
- Test for pending_documents → includes missing doc names in message
- Test for referred claim → includes months_active in message
- Test notification immutability (frozen dataclass)
- Test tuple return type (exactly 2 notifications per call)
- Use descriptive test names following pattern: test_notify_<scenario>_<expectation>

**Sample test methods:**
- test_notify_approved_generates_email_with_confirmation
- test_notify_approved_generates_sms_with_amount
- test_notify_pending_documents_lists_missing_in_email
- test_notify_referred_includes_months_active_in_message
- test_notify_returns_two_notifications_tuple

**Acceptance criteria:**
- All test methods pass
- Each test is focused (tests one scenario/assertion)
- Test names are descriptive
- At least 5 tests covering all decision statuses and both channels

**Dependencies:** Tasks 1, 2, 3 (Claim, Notification, notify_claim_decision must exist)

---

### Task 8: Update existing tests to work with extended Claim
**Files:** `tests/test_claims.py`

**Description:**
Update any existing tests that create Claim objects to include the new email and phone fields. Ensure all existing tests still pass with the extended dataclass.

**Requirements:**
- Locate any test fixtures creating Claim objects
- Add synthetic email and phone values based on Task 1 specification
- Verify all existing tests pass
- No new test logic needed, just adapt existing fixtures

**Acceptance criteria:**
- All existing tests pass
- Claim fixtures include email and phone fields
- Fixtures use synthetic data matching Task 1 specification

**Dependencies:** Tasks 1, 2 (Claim must have email/phone fields; Task 1 defines formats)

---

## Completion Checklist

After all tasks are complete:

- [ ] `specs/claims-notifications/implementation-decisions.md`: Created with all 7 specifications
  - [ ] Contact validator algorithm with accept/reject examples
  - [ ] Transition ID format and generation responsibility
  - [ ] Outbox API signatures
  - [ ] Message template strings for all statuses
  - [ ] Claim reference format
  - [ ] Simulated/synthetic language requirements
  - [ ] Operator guidance for outcome codes
- [ ] `src/dreamguard/claims.py`: Claim extended with email, phone (Task 2)
- [ ] `src/dreamguard/notifications.py`: Created with Notification class and notify_claim_decision() (Task 3)
- [ ] `src/dreamguard/intake.py`: Updated to parse contact details (Task 4)
- [ ] `data/sample_claims.json`: Updated with synthetic contacts (Task 5)
- [ ] `src/dreamguard/__init__.py`: Exports Notification and notify_claim_decision (Task 6)
- [ ] `tests/test_notifications.py`: Comprehensive test suite created (Task 7)
- [ ] `tests/test_claims.py`: Fixtures updated with email/phone (Task 8)
- [ ] All tests pass: `python -m unittest discover -s tests -v`
- [ ] No type hint errors (if running mypy or similar)
- [ ] Code follows PEP 8 and project conventions

**Critical path reminder:**
- Task 1 (implementation-decisions.md) **must** complete first and be reviewed/approved before Tasks 2-8 begin
- Task 1 blocks Tasks 2, 3, 5, 8 (they depend on specifications from implementation-decisions.md)
- Task 2 blocks Task 4 (Claim must have email/phone fields)
- Task 3 blocks Task 6 (notifications.py must exist to export)
- Task 6 can run in parallel with Task 7
