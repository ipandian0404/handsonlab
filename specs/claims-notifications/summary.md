# Claims Status Notifications — Executive Summary

---

## Feature
**Claims Status Notifications**

Extend the DreamGuard assessment service to automatically generate synthetic email and SMS notifications that inform policyholders of their claim decision status.

---

## Key Changes

- **Extended Claim dataclass:** Add synthetic email and phone fields to carry client contact information
- **New Notification dataclass:** Represent email/SMS messages with decision-specific content
- **New notifications.py module:** Contains `notify_claim_decision()` function to generate email + SMS for each decision
- **Updated intake.py:** Parse contact details from JSON
- **Updated sample data:** Add fictional email (*.synthetic domain) and phone (+27... E.164 format) to all claims
- **Public API expansion:** Export Notification and notify_claim_decision()

---

## Message Strategy

Each claim decision triggers two notifications with templated content:

| Status | Email | SMS |
|--------|-------|-----|
| **Approved** | "Your Claim SYN-XXXX Has Been Approved" | "DreamGuard: Your claim SYN-XXXX (R250,000) approved. Payment in 5-7 days." |
| **Pending Documents** | "Additional Documents Required for Claim SYN-XXXX" | "DreamGuard: Missing 1 document for claim SYN-XXXX. Upload now at dreamguard.synthetic." |
| **Referred** | "Your Claim SYN-XXXX Is Under Review" | "DreamGuard: Claim SYN-XXXX under review. Policy active 1 month. Status update in 10 days." |

All contact information is completely synthetic (fictional domains, fictional phone numbers).

---

## Testing Coverage

| Scenario | Test Count | Coverage |
|----------|-----------|----------|
| Approved decision | 2 | Email + SMS generation |
| Pending documents | 2 | List missing docs in messages |
| Referred status | 2 | Include waiting period info |
| Data immutability | 1 | Frozen dataclass |
| Return type | 1 | Always tuple of 2 notifications |
| **Total** | **~8 tests** | All decision types, both channels |

---

## Success Criteria

✓ Claim records carry synthetic contact details (email, phone)
✓ assess_claim() + notify_claim_decision() create appropriate messages
✓ All contact details are fictional (no real domains, numbers, people)
✓ Email and SMS both generated per decision
✓ Code fully type-hinted with comprehensive docstrings
✓ All existing tests pass; new tests provide branch coverage
✓ Public API extended (Notification, notify_claim_decision exported)

---

## Implementation Order

1. **Task 1:** Extend Claim dataclass
2. **Task 2:** Create notifications.py with Notification and notify_claim_decision()
3. **Task 3:** Update intake.py to load contacts
4. **Task 4:** Update sample_claims.json with synthetic details
5. **Task 5:** Update public API
6. **Tasks 6-7:** Create/update tests

**Estimated effort:** 6-8 focused commits, ~2-3 hours for experienced participants

---

## Files Affected

```
src/dreamguard/
  claims.py              (extend Claim)
  notifications.py       (new)
  intake.py              (update load_claims)
  __init__.py            (update exports)

data/
  sample_claims.json     (add email, phone)

tests/
  test_notifications.py  (new)
  test_claims.py         (update fixtures)
```

---

## Design Alignment

- ✓ Immutable dataclasses (frozen)
- ✓ Full type hints on all functions
- ✓ Decimal for monetary amounts in messages
- ✓ Synthetic data only (fictional contacts)
- ✓ PEP 8 naming throughout
- ✓ unittest framework for tests
- ✓ Focused changes (1 commit per task)
- ✓ Public API preserved and extended clearly
