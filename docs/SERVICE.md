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

Rules run in this order:

1. A claim type other than `life` or `disability` returns `rejected`, an approved
	amount of `0`, and the reason `Unsupported claim type: <claim_type>`.
2. A claim with an amount less than or equal to `0` returns `rejected`, an
	approved amount of `0`, and the reason
	`Claim amount must be greater than zero`.
3. A claim with `months_active` below `3` returns `referred`, an approved amount
	of `0`, and the reason `Waiting period review required`.
4. For a claim outside that waiting period, a `life` claim requires
	`death_certificate` and `identity_document`; a `disability` claim requires
	`medical_report` and `identity_document`.
5. If any required documents are absent, the result is `pending_documents` with
	an approved amount of `0`. Reasons are sorted by document identifier and use
	the form `Missing <document>`.
6. Any claim that reaches the final rule returns `approved` for the requested
	amount with no reasons.

The current code validates claim type and amount only. It does not validate
policy numbers, active-policy duration, document names, or JSON shape.

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