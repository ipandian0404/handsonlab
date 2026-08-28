# Claims-Status Notifications — Design Document

**Status:** Ready for Approval  
**Phase:** Design (Phase 2)  
**Date:** 2026-08-28  
**Feature:** Claims-Status Notifications System

---

## 1. Executive Summary

This document defines the architecture for a claims-status notification system that triggers on claim assessment, captures decision context, and delivers notifications to policyholders. The system is designed to be:

- **Extensible:** Support current statuses ("referred", "pending_documents", "approved") with a clean path to add future statuses (e.g., "rejected", "appeals")
- **Pure:** Preserve `assess_claim()` as a side-effect-free pure function; notifications are triggered *after* assessment via a separate event-driven layer
- **Auditable:** Immutable event log for compliance and debugging
- **Type-Safe:** Full type hints, `Decimal` for money, immutable dataclasses
- **Synthetic:** All test data and examples use fictional contacts and policy numbers

---

## 2. System Architecture

### 2.1 High-Level Component Diagram

```
┌──────────────────┐
│   Claim Input    │
│  (JSON/API)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│    assess_claim() — Pure Function    │
│  (No side-effects, returns Decision) │
└────────┬─────────────────────────────┘
         │
         │ ClaimDecision
         │
         ▼
┌──────────────────────────────────────┐
│  Notification Event Trigger           │
│  (Detect status, build context)       │
└────────┬─────────────────────────────┘
         │
         │ NotificationEvent
         │
         ▼
┌──────────────────────────────────────┐
│  Notification Delivery Pipeline       │
│  (Send via channel, log result)       │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│   NotificationLog (Audit Trail)       │
│   (Immutable event storage)           │
└──────────────────────────────────────┘
```

### 2.2 Design Principles

1. **Separation of Concerns:** Assessment logic is decoupled from notification delivery
2. **Purity:** `assess_claim()` has no I/O side-effects; notifications are triggered by an external caller
3. **Extensibility:** Status-to-notification mapping is data-driven, not hardcoded
4. **Immutability:** All event records are immutable; append-only log
5. **Type Safety:** Every input/output has explicit type hints and validation

---

## 3. Data Models

All data models are **immutable dataclasses** with `frozen=True` to prevent accidental state mutation.

### 3.1 ContactDetails

Represents a policyholder's contact information.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ContactDetails:
    """Immutable contact information for a policyholder.
    
    Attributes:
        name: Full name (str, non-empty).
        email: Email address (str, non-empty, valid format).
        phone: Phone number (str, non-empty, valid format).
    
    Raises:
        ValueError: If any field is empty or email/phone format is invalid.
    
    Examples:
        >>> contact = ContactDetails(
        ...     name="Jane Doe",
        ...     email="jane.doe@example.com",
        ...     phone="+1-555-0123"
        ... )
    """
    name: str
    email: str
    phone: str
    
    def __post_init__(self) -> None:
        """Validate contact details on instantiation."""
        if not self.name or not self.name.strip():
            raise ValueError("name must be non-empty")
        if not self.email or not self.email.strip():
            raise ValueError("email must be non-empty")
        if "@" not in self.email:
            raise ValueError("email must contain '@'")
        if not self.phone or not self.phone.strip():
            raise ValueError("phone must be non-empty")
```

**Design Rationale:**
- Validation in `__post_init__` prevents invalid instances from being created
- Basic format checks (email "@", non-empty) without complex regex
- Frozen dataclass ensures contact details cannot be modified after creation
- Error messages are clear and actionable

---

### 3.2 NotificationEvent

Represents a single notification trigger event.

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True)
class NotificationEvent:
    """Immutable record of a notification event.
    
    Triggered when assess_claim() returns a decision, capturing claim context,
    decision status, contact details, and approved amount (if applicable).
    
    Attributes:
        claim_id: Unique identifier for the claim (str).
        claim_type: Type of claim (str, e.g., "auto", "disability").
        status: Decision status (str, e.g., "referred", "pending_documents", "approved").
        contact_details: Policyholder contact information (ContactDetails).
        triggered_at: ISO 8601 timestamp when event was triggered (datetime).
        approved_amount: Amount approved if status is "approved", None otherwise (Decimal or None).
        reasons: Decision reasons from ClaimDecision (tuple of str).
    
    Examples:
        >>> from datetime import datetime
        >>> event = NotificationEvent(
        ...     claim_id="CLM-2024-001",
        ...     claim_type="auto",
        ...     status="approved",
        ...     contact_details=ContactDetails(
        ...         name="John Smith",
        ...         email="john@example.com",
        ...         phone="+1-555-9876"
        ...     ),
        ...     triggered_at=datetime.now(),
        ...     approved_amount=Decimal("2500.00"),
        ...     reasons=()
        ... )
    """
    claim_id: str
    claim_type: str
    status: str
    contact_details: ContactDetails
    triggered_at: datetime
    approved_amount: Decimal | None
    reasons: tuple[str, ...]
```

**Design Rationale:**
- Captures all context needed to compose and send a notification
- `approved_amount` is optional (None for non-approved statuses)
- `reasons` tuple from ClaimDecision provides detailed context
- `triggered_at` enables audit trail and timing analysis
- Frozen and immutable; historical record cannot be altered

---

### 3.3 NotificationLog

Immutable append-only log of notification events.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class NotificationLog:
    """Immutable audit trail of notification events.
    
    Stores a chronological log of all notifications triggered, enabling
    compliance audits and debugging.
    
    Attributes:
        events: Tuple of NotificationEvent objects (immutable sequence).
    
    Methods:
        append(event): Return a new NotificationLog with the event added.
    
    Examples:
        >>> log = NotificationLog()
        >>> event1 = NotificationEvent(...)
        >>> log = log.append(event1)
        >>> len(log.events)
        1
    """
    events: tuple[NotificationEvent, ...] = field(default_factory=tuple)
    
    def append(self, event: NotificationEvent) -> "NotificationLog":
        """Append an event to the log, returning a new NotificationLog.
        
        Args:
            event: NotificationEvent to add to the log.
        
        Returns:
            A new NotificationLog with the event appended.
        """
        return NotificationLog(events=self.events + (event,))
```

**Design Rationale:**
- Immutable tuple prevents accidental modification
- `append()` returns a new instance (functional style) rather than mutating
- Enables transaction-like semantics: accept the new log or discard it
- Frozen dataclass reinforces immutability contract

---

## 4. Integration with assess_claim()

### 4.1 Current assess_claim() Signature (Unchanged)

```python
from dreamguard import Claim, ClaimDecision

def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a claim and return a decision without modifying the claim.
    
    Pure function: no side-effects, deterministic, testable.
    Notification sending is triggered externally by the caller.
    
    Args:
        claim: A Claim object to assess.
    
    Returns:
        A ClaimDecision with status, approved_amount, and reasons.
    """
    # ... existing implementation ...
```

### 4.2 ContactDetails Integration with Claim

**Option A (Recommended): Add Optional ContactDetails to Claim**

Extend the Claim model to optionally include contact details:

```python
@dataclass(frozen=True)
class Claim:
    """..."""
    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]
    contact_details: ContactDetails | None = None  # NEW
```

**Rationale:**
- Claim data naturally includes contact info
- Backward compatible: `None` default allows existing code to work
- Single, unified model for claim context
- Notification layer can extract contact details after assessment

**Option B (Alternative): Pass Contact Info Separately**

Keep Claim unchanged; pass contact details to a wrapper function:

```python
def assess_and_notify(claim: Claim, contact: ContactDetails) -> ClaimDecision:
    """Assess claim and return decision; caller responsible for notifications."""
    decision = assess_claim(claim)
    # Caller handles notification triggering
    return decision
```

**Rationale:**
- Preserves existing Claim contract strictly
- Cleaner separation: assessment is pure, notification context is external
- May feel more verbose for users who always provide contacts

**Recommendation:** Use Option A. The contact details are intrinsic to the claim context and enable a cleaner API.

### 4.3 Notification Triggering Workflow

After `assess_claim()` returns a `ClaimDecision`, the caller (or a post-assessment hook) triggers notifications:

```python
def handle_claim_assessment(claim: Claim) -> tuple[ClaimDecision, NotificationEvent | None]:
    """Assess a claim and trigger notifications if contact details are provided.
    
    Args:
        claim: A Claim object (may include contact_details).
    
    Returns:
        A tuple of (ClaimDecision, NotificationEvent or None).
    
    Examples:
        >>> claim = Claim(
        ...     policy_number="POL-2024-001",
        ...     claim_type="auto",
        ...     amount=Decimal("2500.00"),
        ...     months_active=6,
        ...     documents=("police_report",),
        ...     contact_details=ContactDetails(
        ...         name="Alice Smith",
        ...         email="alice@example.com",
        ...         phone="+1-555-0001"
        ...     )
        ... )
        >>> decision, event = handle_claim_assessment(claim)
        >>> decision.status
        'approved'
        >>> event.triggered_at  # Not None if contact_details provided
    """
    decision = assess_claim(claim)
    
    # Build notification event if contact details are present
    event = None
    if claim.contact_details:
        event = NotificationEvent(
            claim_id=f"CLM-{claim.policy_number}",  # Example ID scheme
            claim_type=claim.claim_type,
            status=decision.status,
            contact_details=claim.contact_details,
            triggered_at=datetime.now(timezone.utc),
            approved_amount=decision.approved_amount if decision.status == "approved" else None,
            reasons=decision.reasons
        )
    
    return decision, event
```

**Rationale:**
- `assess_claim()` remains pure with no side-effects
- Notification is triggered *after* assessment, decoupled from decision logic
- Returns both decision and event for flexibility (can ignore event if not needed)
- Supports optional contact details gracefully

---

## 5. Notification Delivery Design

### 5.1 Notification Delivery Interface (Strategy Pattern)

Define an abstract interface for notification delivery channels:

```python
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    """Abstract base for notification delivery channels.
    
    Implementations provide concrete delivery mechanisms (email, SMS, etc).
    """
    
    @abstractmethod
    def send(self, event: NotificationEvent) -> None:
        """Send a notification for the given event.
        
        Args:
            event: NotificationEvent to send.
        
        Raises:
            NotificationError: If delivery fails.
        """
        pass
```

### 5.2 Concrete Implementations (Training/Mock)

For DreamGuard training environment, use mock implementations:

```python
class MockEmailChannel(NotificationChannel):
    """Mock email delivery (prints to console/log)."""
    
    def send(self, event: NotificationEvent) -> None:
        """Log notification as if sending email."""
        print(
            f"[EMAIL] To: {event.contact_details.email}\n"
            f"Subject: Claim {event.claim_id} Status: {event.status}\n"
            f"Body: Your {event.claim_type} claim is {event.status}."
        )

class MockSmsChannel(NotificationChannel):
    """Mock SMS delivery (prints to console/log)."""
    
    def send(self, event: NotificationEvent) -> None:
        """Log notification as if sending SMS."""
        print(
            f"[SMS] To: {event.contact_details.phone}\n"
            f"Your claim {event.claim_id} is {event.status}."
        )
```

### 5.3 Notification Dispatcher

Central coordinator that routes events to appropriate channels:

```python
class NotificationDispatcher:
    """Routes notification events to delivery channels."""
    
    def __init__(self, channels: dict[str, NotificationChannel]):
        """Initialize with a mapping of status to channels.
        
        Args:
            channels: Dict mapping status (e.g., "approved") to NotificationChannel.
                Example: {"approved": email_channel, "referred": sms_channel}
        """
        self.channels = channels
    
    def dispatch(self, event: NotificationEvent, log: NotificationLog) -> NotificationLog:
        """Dispatch event to appropriate channel and log result.
        
        Args:
            event: NotificationEvent to dispatch.
            log: Current NotificationLog (will be updated).
        
        Returns:
            Updated NotificationLog with the event added.
        """
        # Route based on status
        if event.status in self.channels:
            channel = self.channels[event.status]
            try:
                channel.send(event)
            except Exception as e:
                # Log error but don't fail; event still logged for audit
                print(f"Warning: Delivery failed for {event.claim_id}: {e}")
        
        # Always log event, regardless of delivery success
        return log.append(event)
```

**Design Rationale:**
- Strategy pattern allows flexible channel implementations
- Dispatcher decouples notification logic from delivery mechanism
- Mock channels suitable for training (no actual email/SMS)
- Append-only log preserves full history even if delivery fails

---

## 6. Storage and Audit Trail Design

### 6.1 In-Memory Audit Log

For the training system, maintain an in-memory `NotificationLog`:

```python
class NotificationService:
    """Service managing notification events and audit log."""
    
    def __init__(self, dispatcher: NotificationDispatcher):
        """Initialize with a dispatcher and empty log.
        
        Args:
            dispatcher: NotificationDispatcher for routing events.
        """
        self.dispatcher = dispatcher
        self.log = NotificationLog()  # Immutable, append-only
    
    def send_notification(self, event: NotificationEvent) -> None:
        """Send notification and log the event.
        
        Args:
            event: NotificationEvent to send and log.
        """
        self.log = self.dispatcher.dispatch(event, self.log)
    
    def get_log(self) -> NotificationLog:
        """Retrieve the current audit log.
        
        Returns:
            NotificationLog containing all events.
        """
        return self.log
```

### 6.2 Log Persistence (Future Extension)

For production, persist the log to JSON or database:

```python
def save_log_to_json(log: NotificationLog, path: str) -> None:
    """Serialize NotificationLog to JSON file.
    
    Future: Implement when persistence is required.
    """
    pass

def load_log_from_json(path: str) -> NotificationLog:
    """Deserialize NotificationLog from JSON file.
    
    Future: Implement when persistence is required.
    """
    pass
```

**Design Rationale:**
- In-memory log sufficient for training/demo
- Immutable structure prevents accidental corruption
- JSON serialization path enables future persistence
- Audit trail enables compliance and debugging

---

## 7. Extensibility for Future Statuses

### 7.1 Status-to-Channel Mapping

Use configuration to map statuses to notification channels:

```python
# In a config module or initialization code
NOTIFICATION_CHANNELS = {
    "referred": MockEmailChannel(),        # Current
    "pending_documents": MockEmailChannel(),  # Current
    "approved": MockEmailChannel(),         # Current
    # Future statuses can be added without code changes:
    # "rejected": MockEmailChannel(),
    # "appeals": MockSmsChannel(),
}

dispatcher = NotificationDispatcher(NOTIFICATION_CHANNELS)
```

### 7.2 Adding New Statuses

To add a new status (e.g., "rejected"):

1. **Update config:** Add the new status to `NOTIFICATION_CHANNELS`
2. **No code changes needed:** Existing `NotificationEvent` and `NotificationDispatcher` work unchanged
3. **Update decision rules:** Only `assess_claim()` logic needs extension (outside scope of this design)

**Rationale:**
- Configuration-driven approach avoids hardcoded status lists
- New statuses integrate seamlessly with existing notification pipeline
- Minimal refactoring required for future features

---

## 8. Error Handling and Validation

### 8.1 ContactDetails Validation

Errors on invalid input:

```python
try:
    contact = ContactDetails(name="", email="alice@example.com", phone="+1-555-0001")
except ValueError as e:
    print(f"Invalid contact: {e}")  # "Invalid contact: name must be non-empty"
```

### 8.2 Notification Delivery Errors

Errors logged but don't fail the audit trail:

```python
def dispatch(self, event: NotificationEvent, log: NotificationLog) -> NotificationLog:
    if event.status in self.channels:
        try:
            self.channels[event.status].send(event)
        except Exception as e:
            # Log warning, but append event to log anyway
            print(f"Delivery warning: {e}")
    
    return log.append(event)  # Event logged regardless
```

**Rationale:**
- Contact validation prevents propagation of bad data
- Delivery errors don't block logging; audit trail is always maintained
- Operators can investigate delivery failures via the log

---

## 9. Trade-offs and Alternatives

### 9.1 ContactDetails in Claim vs. Separate

| Aspect | In Claim (Recommended) | Separate Parameter |
|--------|------------------------|-------------------|
| **Naturality** | Contacts belong with claim data | Feels external to claim |
| **API Simplicity** | Single object to pass | Two arguments |
| **Backward Compat** | Optional field (None default) | Requires wrapper function |
| **Purity** | assess_claim() still pure | assess_claim() still pure |

**Decision:** In Claim (Option A). Simpler API, backward compatible, data integrity.

### 9.2 In-Memory vs. Persistent Log

| Aspect | In-Memory | Persistent (JSON/DB) |
|--------|-----------|----------------------|
| **Simplicity** | Minimal code | More infrastructure |
| **Durability** | Lost on restart | Survives failures |
| **Training Fit** | Good for demos | Better for audit trails |
| **Scalability** | Limited by RAM | Scales with storage |

**Decision:** In-Memory for Phase 3. Persist option documented for Phase 4 (future).

### 9.3 Notification Triggering Model

| Model | Where Triggered | Pros | Cons |
|-------|-----------------|------|------|
| **Explicit (Recommended)** | Caller explicitly sends event | Full control, testable | Caller must know to send |
| **Implicit Hook** | Auto-triggered inside assess_claim() | Automatic, no caller code | assess_claim() side-effects |
| **Event Bus** | Pub/sub after assessment | Decoupled, scalable | More complexity |

**Decision:** Explicit triggering (recommended). Preserves assess_claim() purity.

---

## 10. Implementation Roadmap

### Phase 3 (Tasks Breakdown)
1. Implement `ContactDetails` dataclass with validation
2. Implement `NotificationEvent` dataclass
3. Implement `NotificationLog` with append semantics
4. Implement abstract `NotificationChannel` interface
5. Implement `MockEmailChannel` and `MockSmsChannel`
6. Implement `NotificationDispatcher` routing logic
7. Implement `NotificationService` coordinating service
8. Add `contact_details` field to `Claim` (optional, backward compatible)
9. Implement `handle_claim_assessment()` integration function
10. Write comprehensive unit tests for all components
11. Create synthetic sample data and integration examples

### Phase 4 (Future: Not Included)
- Persistent storage (JSON, database)
- Real email/SMS delivery implementations
- Notification scheduling and retry logic
- Webhook delivery channel
- Analytics and reporting on notifications

---

## 11. Summary

The claims-status notification system is designed as an **event-driven layer** that sits *after* claim assessment, capturing decision context and routing notifications to configured channels. Key design principles:

✅ **Pure Functions:** `assess_claim()` remains side-effect-free  
✅ **Extensible:** New statuses integrate via configuration, no code refactoring  
✅ **Immutable:** All models frozen; audit log append-only  
✅ **Type-Safe:** Full type hints, `Decimal` for money, validation at boundaries  
✅ **Auditable:** Immutable event log preserves history for compliance  
✅ **Synthetic Data:** All examples use fictional contacts and policies  
✅ **DreamGuard Standards:** Follows PEP 8, immutable dataclasses, public API contract preserved

---

## Approval Gate

**Ready for review.** Once approved, Phase 3 (Tasks + Executive Summary) will break this design into granular development tasks and create a stakeholder-facing summary.

**Reviewer Guidance:**
- Verify data models support current and future statuses
- Confirm assess_claim() purity is preserved
- Check that extensibility path is clear (adding new statuses)
- Review error handling approach
- Validate trade-off decisions
