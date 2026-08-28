# Claims Status Notifications — Phase 2: Design

**Status:** Pending approval

---

## Architecture

The notification system extends the existing claims assessment pipeline:

```
┌─────────────────────────────────────┐
│  Load Claim (with contact details)  │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │assess_claim()│
        └──────┬───────┘
               │
               ▼
┌──────────────────────────────┐
│ notify_claim_decision()      │
│ (creates notifications)      │
└──────────────────────────────┘
               │
               ▼
      ┌─────────────────┐
      │  Notifications  │
      │  (email + SMS)  │
      └─────────────────┘
```

---

## New/Modified Components

### 1. Extended `Claim` dataclass
- **Responsibility:** Carry synthetic client contact information alongside claim data
- **New fields:**
  - `email: str` — Synthetic email address
  - `phone: str` — Synthetic phone number (E.164 format, e.g., "+27115551234")

### 2. New `Notification` dataclass
- **Responsibility:** Represent a generated notification message
- **Fields:**
  - `policy_number: str` — Policy associated with this notification
  - `channel: str` — Delivery channel ("email" or "sms")
  - `recipient: str` — Recipient contact (email or phone)
  - `subject: str` — Notification subject (for email)
  - `message: str` — Message body
  - `decision_status: str` — Status that triggered the notification

### 3. New `notify_claim_decision()` function
- **Responsibility:** Generate notifications when a claim is assessed
- **Signature:**
  ```python
  def notify_claim_decision(
      claim: Claim,
      decision: ClaimDecision
  ) -> tuple[Notification, ...]
  ```
- **Behavior:**
  - Takes an assessed claim and its decision
  - Generates two notifications per claim: one email, one SMS
  - Uses decision-specific message templates
  - Returns tuple of Notification objects (immutable)

### 4. Message templates (decision-specific)

**Approved:**
- Email subject: "Your Claim SYN-XXXX Has Been Approved"
- Email body: "Good news! Your {claim_type} claim of {amount} has been approved. You can expect payment within 5-7 business days."
- SMS: "DreamGuard: Your claim SYN-XXXX ({amount}) approved. Payment in 5-7 days. Ref: {decision_id}"

**Pending Documents:**
- Email subject: "Additional Documents Required for Claim SYN-XXXX"
- Email body: "We need additional documents to process your claim: {missing_docs_list}. Please upload them to your account."
- SMS: "DreamGuard: Missing {count} documents for claim SYN-XXXX. Upload now at dreamguard.synthetic."

**Referred:**
- Email subject: "Your Claim SYN-XXXX Is Under Review"
- Email body: "Your claim is being reviewed. Waiting period requires 3 months of active policy. Current: {months_active} months. We'll follow up soon."
- SMS: "DreamGuard: Claim SYN-XXXX under review. Policy active {months_active} months. Status update in 10 days."

---

## Key Interfaces

### Updated Claim dataclass
```python
@dataclass(frozen=True)
class Claim:
    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]
    email: str              # NEW
    phone: str              # NEW
```

### New Notification dataclass
```python
@dataclass(frozen=True)
class Notification:
    policy_number: str
    channel: str            # "email" or "sms"
    recipient: str          # email or phone
    subject: str            # email only
    message: str
    decision_status: str
```

### New notify function
```python
def notify_claim_decision(
    claim: Claim,
    decision: ClaimDecision
) -> tuple[Notification, ...]:
    """Generate email and SMS notifications for a claim decision."""
```

---

## Data Structures

### Contact field constraints
- **Email:** Must contain `@` and a domain ending in `.synthetic`, `.test`, or similar fictional pattern
- **Phone:** Must be E.164 format (+{country}{number}), all synthetic numbers
- **Validation:** No real-world email domains or phone number ranges allowed

### Notification channel enum (future)
Could use `Literal["email", "sms"]` for type safety in current Python 3.10+

---

## Dependencies

### Internal
- `Claim` (existing, extended)
- `ClaimDecision` (existing)
- `Decimal` (existing, for amounts in message formatting)

### External
- None (no SMTP, SMS gateway, or HTTP libraries required)
- `dataclasses` (standard library)
- `decimal` (standard library)

---

## Constraints & Assumptions

- **Immutability:** Both Claim and Notification are frozen dataclasses
- **Type hints:** All functions must be fully annotated
- **Decimal for money:** Amounts formatted from Decimal, never float
- **Synthetic data only:** Email domains, phone numbers, all fictional
- **PEP 8 naming:** snake_case for functions, PascalCase for classes
- **No external services:** Notifications are generated, not delivered
- **Deterministic:** Same input always produces same notification content

---

## Testing Strategy

### Test scenarios to cover
1. **Approved claim** → generates email + SMS with approval messaging
2. **Pending documents** → generates notifications listing missing documents
3. **Referred claim** → generates notifications about waiting period
4. **Contact validation** → rejects real-world email domains/phone ranges (future stricter validation)
5. **Notification immutability** → Notification objects are frozen
6. **Tuple return type** → Function always returns tuple of notifications

### Sample test names
- `test_notify_approved_claim_generates_email_and_sms`
- `test_notify_pending_documents_lists_missing_items`
- `test_notify_referred_includes_months_active`
- `test_notification_objects_are_frozen`

---

## Integration with existing code

- `Claim` in `claims.py` will be extended (new frozen dataclass fields added)
- `load_claims()` in `intake.py` will be updated to parse email/phone from JSON
- New `notify_claim_decision()` in new `notifications.py` module
- Public API update: `dreamguard/__init__.py` exports `Notification` and `notify_claim_decision`
- Sample claims JSON updated with synthetic contact details

---

## Next steps

After design approval:
1. Implement extended Claim with contact fields
2. Create notifications.py with Notification class and notify_claim_decision() function
3. Update intake.py to load contact details
4. Update public API exports
5. Update sample_claims.json with synthetic contacts
6. Create comprehensive unit tests
