# Claims Status Notifications — Phase 1: Intent

**Status:** ✓ Approved

---

## Feature
Claims Status Notifications

## Objective
Automatically send synthetic notifications (email and SMS) to policyholders when their claim assessment completes, informing them of the decision status and any required next steps.

## User/Consumer
- **Primary:** Policyholders (synthetic clients with fictional contact details)
- **Secondary:** DreamGuard assessment service (internal)

## Value
- **Engagement:** Keeps policyholders informed in real-time about claim status
- **Workflow clarity:** Different notification content guides clients on what happens next based on decision (approved, pending documents, referred, etc.)
- **Training scope:** Demonstrates how assessment outcomes integrate with downstream systems (notifications, communications)

## Scope

### Included
- Extend `Claim` dataclass to include synthetic contact details (email address, phone number)
- Create `Notification` dataclass representing a notification message
- Create `notify_claim_decision()` function that generates notifications after assessment
- Support two delivery channels: email and SMS
- Include decision-specific message templates based on status (approved, pending_documents, referred)
- Validate all contact details are synthetic (fictional domains, number formats)
- Load claims with contact details from updated JSON format

### Not Included (future work)
- Actual email/SMS delivery (no SMTP, no SMS gateway integration)
- Notification delivery logs or persistence
- Retry logic or delivery confirmation
- Templating engine beyond basic Python string formatting
- User preferences (e.g., opt-out, channel preference)
- Multi-language support

## Success Criteria
- Claim records can include synthetic email and phone fields
- After `assess_claim()` returns a decision, `notify_claim_decision()` generates appropriate notifications
- Notifications contain decision-specific messaging
- All contact details are fictional and clearly marked as synthetic
- Both email and SMS notifications are generated for appropriate statuses
- Code includes comprehensive docstrings and full type hints
- Test coverage demonstrates notification generation for all decision types
