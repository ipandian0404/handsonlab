# Claims Status Notifications — Intent

**Feature Name:** Claims Status Notifications  
**Date Created:** 2026-08-28  
**Status:** Intent Phase

---

## Executive Summary

The Claims Status Notifications feature extends DreamGuard's claims assessment system with automated notification capabilities. When a claim's assessment status changes, the system will send a synthetic notification to the claimant with their claim status update. This feature demonstrates event-driven architecture, immutable event models, and integration with the existing assessment pipeline while maintaining DreamGuard's commitment to synthetic-data-only training scenarios.

---

## Purpose & Scope

### Primary Purpose
Enable DreamGuard to notify claimants about their claim status changes in a deterministic, trainable manner using synthetic contact details.

### Scope — In
- Trigger notifications when claim status transitions to specific states: `"pending"`, `"referred"`, `"approved"`, or `"rejected"`
- Provide synthetic contact details (name, email, phone) for notification delivery
- Integrate with the existing `assess_claim()` pipeline
- Log or store notification events for audit/training purposes
- Maintain immutable, type-safe event models aligned with DreamGuard patterns

### Scope — Out
- **Not production email/SMS delivery**: Notifications are logged/stored, not sent to actual endpoints
- **Not customer-facing dashboard**: No UI or external communication
- **Not notification templating or localization**: Use simple, fixed message formats
- **Not retry logic or delivery confirmation**: One-shot logging is sufficient for training

---

## Stakeholders

| Role | Involvement | Expectations |
|------|-----------|--------------|
| **Training Participants** | Primary end user | Learn how to integrate notifications into claim assessment pipelines |
| **DreamGuard Maintainers** | Code reviewers & design critics | Ensure coding standards (PEP 8, Decimal, immutable models), synthetic data only |
| **Copilot Users** | Tool consumers | Use this feature as a reference for GitHub Copilot-assisted development workflows |

---

## User Stories

### Story 1: Receive Notification on Claim Approval
**As a** claimant (represented by synthetic contact details)  
**I want** to be notified when my claim is approved  
**So that** I can track my claim progress in the system

**Acceptance Criteria:**
- When `assess_claim()` returns status `"approved"`, a notification is created
- Notification includes claim decision details (status, approved amount)
- Synthetic contact details are included in the notification
- Notification is logged/stored for audit purposes

---

### Story 2: Receive Notification on Waiting Period Referral
**As a** claimant  
**I want** to be notified when my claim is referred for waiting period review  
**So that** I understand the reason for the status and know when to expect a final decision

**Acceptance Criteria:**
- When `assess_claim()` returns status `"referred"`, a notification is created
- Notification includes the reason (e.g., "Waiting period review required")
- Synthetic contact details are included
- Notification is logged/stored

---

### Story 3: Receive Notification on Pending Documents
**As a** claimant  
**I want** to be notified when my claim requires additional documentation  
**So that** I can submit missing documents and complete my claim

**Acceptance Criteria:**
- When `assess_claim()` returns status `"pending_documents"`, a notification is created
- Notification lists missing documents (e.g., "Missing medical_report")
- Synthetic contact details are included
- Notification is logged/stored

---

### Story 4: Audit Notification Events
**As a** training participant  
**I want** to see all notifications that have been generated  
**So that** I can verify the notification system is integrated correctly with the assessment pipeline

**Acceptance Criteria:**
- All notifications are logged with timestamp, claim details, and contact info
- Notifications can be queried or retrieved for inspection
- Log format is machine-readable for test validation

---

## Success Criteria

### Functional
- ✅ Notification system triggers on all four target statuses: `"pending"`, `"referred"`, `"approved"`, `"rejected"`
- ✅ Notifications include synthetic contact details (name, email, phone)
- ✅ Notifications include claim decision data (status, approved amount, reasons)
- ✅ Notification events are immutable and type-safe (frozen dataclass)
- ✅ Integration with `assess_claim()` is non-invasive and testable

### Code Quality
- ✅ All code follows PEP 8 naming (snake_case functions, PascalCase classes)
- ✅ All public functions have type hints and docstrings
- ✅ Monetary amounts use `Decimal`, never `float`
- ✅ Immutable collections use `tuple`, not lists
- ✅ All test fixtures use synthetic data only (no real names, emails, policy numbers)

### Testing & Documentation
- ✅ Unit tests for notification creation and event logging
- ✅ Integration tests verifying notifications trigger on assessment results
- ✅ Test data uses fictional scenarios (e.g., "POL-2024-001", "jane.doe@example.com")
- ✅ Docstrings document synthetic-data-only constraints
- ✅ Module-level docstrings explain notification flow

---

## Constraints & Assumptions

### Constraints
1. **Synthetic Data Only**: All contact details, policy numbers, and claim amounts must be fictional
2. **No External Integration**: Notifications are logged/stored locally, not sent externally
3. **Public API Preservation**: Must not break or rename existing `Claim`, `ClaimDecision`, or `assess_claim()` symbols
4. **Immutable Models**: All notification data models must be frozen dataclasses with tuple fields for collections
5. **Deterministic**: Notification logic must be pure functions (no random UUIDs, non-deterministic timestamps in tests)

### Assumptions
1. The existing `assess_claim()` function will continue to return statuses: `"referred"`, `"pending_documents"`, `"approved"`
   - New status `"rejected"` is NOT currently in the codebase; it is included in requirements but may require future discussion
2. Contact details will be provided alongside or embedded in the claim assessment workflow
3. Notification events do not require real-time delivery; batched/logged delivery is acceptable
4. Training participants will inspect notification logs as part of unit tests

---

## Dependencies & Risks

### Dependencies
- **Existing**: `dreamguard.claims.Claim`, `dreamguard.claims.ClaimDecision`, `dreamguard.assess_claim()`
- **New**: Notification models and event logging mechanism (to be designed in Phase 2)

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Status value mismatch (e.g., system uses `"pending"` vs. assessment uses `"pending_documents"`) | Medium | High | Design phase must align trigger statuses with actual assessment output; verify via tests |
| Over-coupling notifications to claim assessment logic | Medium | Medium | Use event-driven pattern; notifications are triggered *after* assessment, not during |
| Synthetic data quality (e.g., missing contact fields in test fixtures) | Low | Low | Establish test data factory with consistent fictional schemas |
| Scope creep (e.g., actual email delivery) | Low | High | Strict adherence to scope-out items; log-based design prevents accidental external calls |

---

## Next Steps

**Phase 1 Approval Gate:**  
- [ ] Stakeholders review and approve intent
- [ ] Clarify status values ("rejected" inclusion)
- [ ] Confirm contact detail schema (name, email, phone only, or more?)

**Proceeding to Phase 2 (Design):**  
Once intent is approved, the design phase will:
1. Define notification event data models
2. Design the notification trigger mechanism and integration points
3. Specify logging/storage mechanism
4. Document data transformations from `ClaimDecision` to `Notification`

---

## Appendix: Relevant Code References

- **Public API**: [src/dreamguard/__init__.py](../../../src/dreamguard/__init__.py)
- **Core Models & Functions**: [src/dreamguard/claims.py](../../../src/dreamguard/claims.py)
- **Coding Standards**: [.github/copilot-instructions.md](../../../.github/copilot-instructions.md)
- **Claims Decision Rules**: [docs/SERVICE.md](../../../docs/SERVICE.md)
