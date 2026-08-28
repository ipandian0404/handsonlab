# DreamGuard Claims Service

## Purpose

DreamGuard Claims is a small training service that converts claim records into
deterministic assessment decisions. Engineers can use its output to exercise
documentation, testing, and GitHub Copilot workflows. It is not a production
claims processor and does not communicate with customers or external systems.

## Architecture

- `Claim` is an immutable input model containing a policy number, claim type,
  requested `Decimal` amount, active-policy duration, and document identifiers.
- `ClaimDecision` is an immutable output model containing a status, approved
  amount, and explanatory reasons.
- `assess_claim` applies the decision rules to one `Claim` without modifying it.
- `load_claims` is the JSON intake boundary. It reads a top-level JSON array,
  converts each `amount` value to `Decimal`, converts each `documents` value to
  a tuple, and returns a list of `Claim` objects.
- `dreamguard.__init__` exposes `Claim`, `ClaimDecision`, `assess_claim`, and
  `load_claims` as the package's public API.

## Claims decision rules

Rules are applied in this order:

1. If `months_active` is less than 3, returns `referred` with an approved amount of
   `0` and the reason `Waiting period review required`.
2. For a claim with `months_active` of 3 or more, a `life` claim requires
   `death_certificate` and `identity_document`; a `disability` claim requires
   `medical_report` and `identity_document`. Claims with other types are
   processed further (no claim-type validation at this step).
3. If any required documents are absent, the result is `pending_documents` with
   an approved amount of `0`. Reasons are sorted by document identifier and use
   the form `Missing <document>`.
4. Any claim that reaches the final step returns `approved` with the requested
   amount and no reasons.

**Important:** The current implementation validates only whether required documents
are present. It does not validate claim type, claim amount, policy numbers,
active-policy duration, or JSON input shape. Validation of claim type and amount
is planned for future implementation.

## Data and privacy

Every record in this repository is synthetic. Only fictional policy numbers,
claim details, documents, and monetary values may be added. Do not use real
customer, identity, health, policy, contact, or financial information.

## Running the tests

From the repository root, run:

```powershell
python -m unittest discover -s tests -v
python scripts/score.py
```

The starter test suite verifies approval of a complete life claim and loading
of the synthetic sample file. The scorecard reports progress across the four
challenge stages; a low score is expected before participants complete them.