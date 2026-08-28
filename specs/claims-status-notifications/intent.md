# Claims Status Notifications - Intent

## Phase and status

- Phase: 1 - Intent
- Feature slug: `claims-status-notifications`
- Specification status: Proposed, awaiting Phase 1 approval

## Problem

DreamGuard deterministically assesses synthetic claims but does not communicate
assessment outcomes to clients or external systems. A client therefore has no
notification when a claim becomes pending, referred, approved, or rejected.

## Repository evidence

### Confirmed current behavior

- `ClaimDecision.status` is a string produced by `assess_claim`.
- The assessor currently produces `pending_documents`, `referred`, and
  `approved` decisions.
- `pending_documents` means required documents are missing for an otherwise
  eligible life or disability claim. The client-facing request calls this
  state "pending."
- `referred` is produced when `months_active` is below three.
- `approved` is the final outcome for every claim that is neither referred nor
  missing required documents.
- The current assessor explicitly does not produce a rejection outcome.
- `Claim` has no client identity or contact fields, intake loads no contact
  details, and the service does not communicate with clients or external
  systems.
- Repository policy requires all claim and contact details to be synthetic.

### Proposed behavior

- Notify a client when a claim decision enters a supported notifiable status.
- Cover client-facing pending, referred, approved, and rejected notifications.
- Interpret the existing `pending_documents` decision as the requested
  client-facing pending status unless a later approved design defines a new
  domain status.
- Use only explicitly synthetic contact details and synthetic claim data.
- Give each notification enough status information for the synthetic client to
  understand the outcome without exposing unnecessary claim information.
- Treat rejection notification support as conditional on an explicitly defined
  rejection source or rule; Phase 1 does not add or infer a rejection rule.

## Goals

- Define an unambiguous notification requirement for each requested claim
  outcome.
- Preserve the current deterministic assessment behavior unless rejection is
  separately specified and approved.
- Keep contact data synthetic and minimize the claim information included in a
  notification.
- Make notification outcomes observable and testable without requiring real
  customer communication.

## Non-goals

- Implementing notification code, transport integrations, or assessment rules
  in this phase.
- Selecting email, SMS, in-app messaging, or a third-party provider before the
  notification channel is approved.
- Defining why or when a claim is rejected.
- Replacing `pending_documents` with a new assessment status without an
  explicit compatibility decision.
- Sending messages to real people or using production customer data.
- Turning DreamGuard into a production claims processor.

## Users and stakeholders

- Primary user: a fictional client who needs a clear update about a synthetic
  claim.
- Operational stakeholder: a DreamGuard training operator who needs to verify
  that the expected notification was produced.
- Engineering stakeholder: maintainers of claims assessment, JSON intake, and
  the public package API.
- Privacy stakeholder: repository owners responsible for ensuring that only
  synthetic contact and claim data is used.

## Constraints

- Python 3.10+ and the standard library are the current runtime baseline.
- Existing assessment behavior and public exports must remain stable unless a
  later approved specification explicitly changes them.
- Money must remain represented by `Decimal`.
- Assessment and notification behavior must be deterministic and testable.
- Contact details, policy numbers, identities, health details, and financial
  values must be fictional and explicitly synthetic.
- Notification content must not include more claim or contact information than
  is necessary to identify the synthetic claim and communicate its status.
- Rejection cannot be represented as existing supported behavior.

## Assumptions

- A status notification is associated with one synthetic claim decision and
  one synthetic client contact destination.
- "Becomes" means a notification should correspond to a status transition, not
  every repeated read or assessment of an unchanged status; the persistence or
  deduplication mechanism remains unresolved.
- The status vocabulary shown to a client may differ from internal status
  values, specifically `pending_documents` displayed as pending.
- Notification delivery may initially be simulated for the training package,
  subject to approval of the channel and delivery semantics.

## Risks

- Inventing a rejection trigger could silently change assessment behavior and
  conflict with the documented rule set.
- Reassessing an unchanged claim could create duplicate notifications unless
  transition identity or idempotency is defined.
- Adding contact details directly to `Claim` could mix intake, domain, and
  communication responsibilities or break callers.
- Status wording could expose sensitive claim reasons or confuse clients if
  internal and client-facing vocabularies are not mapped explicitly.
- A simulated delivery mechanism could be mistaken for real delivery unless
  its result and limitations are clear.

## Measurable acceptance criteria

- **AC-1:** Given a synthetic claim whose decision changes to
  `pending_documents`, one client-facing pending notification is produced for
  the configured synthetic contact destination.
- **AC-2:** Given a synthetic claim whose decision changes to `referred`, one
  referred notification is produced for the configured synthetic contact
  destination.
- **AC-3:** Given a synthetic claim whose decision changes to `approved`, one
  approved notification is produced for the configured synthetic contact
  destination.
- **AC-4:** Given an explicitly supported rejection decision source, one
  rejected notification is produced for the configured synthetic contact
  destination; no rejection decision rule is implied by this criterion.
- **AC-5:** Reprocessing the same claim without a status change does not produce
  another notification for that unchanged status.
- **AC-6:** Each notification identifies the synthetic claim, communicates a
  client-facing status consistent with the decision, and excludes unnecessary
  claim details.
- **AC-7:** Missing or invalid contact details do not result in attempted
  delivery and produce a deterministic, observable outcome for the operator.
- **AC-8:** Examples, fixtures, logs, and notification destinations used for the
  feature are explicitly synthetic and contain no real personal, policy,
  health, contact, or financial data.
- **AC-9:** Existing `pending_documents`, `referred`, and `approved` assessment
  results remain unchanged unless a later approved design explicitly defines a
  compatible contract change.

## Unresolved questions

1. Which notification channel or simulated delivery boundary is required:
   email, SMS, in-app, an in-memory/outbox record, or another mechanism?
2. Where should synthetic contact details enter and live without coupling them
   unnecessarily to the immutable `Claim` domain model?
3. What authoritative component can produce a rejected decision, and is adding
   a rejection assessment rule in scope for this feature or a prerequisite?
4. What client-facing message content is required for each status, including
   whether reasons or approved amounts may be included?
5. How should status transitions and duplicate suppression be identified when
   the current service has no persistence or claim event history?
6. What should the observable failure states be for invalid contact details and
   failed or unavailable delivery?
7. Is one synthetic contact destination sufficient per claim, or must multiple
   channels or recipients be supported?

## Phase boundary

This artifact records intent only. Architecture, interfaces, data flow, error
contracts, and implementation tasks require Phase 1 approval before they are
defined.