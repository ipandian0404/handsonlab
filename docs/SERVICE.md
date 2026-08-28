# DreamGuard Claims Service

## Purpose

DreamGuard Claims is a small training service that converts claim records into
deterministic assessment decisions. Engineers can use its output to exercise
documentation, testing, and GitHub Copilot workflows. It is not a production
claims processor and does not communicate with customers or external systems.

**Every record in this repository is synthetic.** Only fictional policy numbers,
claim details, documents, and monetary values may be added. Do not use real
customer, identity, health, policy, contact, or financial information.

## Architecture

- `Claim` is an immutable input model containing a policy number, claim type,
  requested `Decimal` amount, active-policy duration, and document identifiers.
- `ClaimDecision` is an immutable output model containing a status, approved
  amount, and explanatory reasons.
- `assess_claim()` applies the decision rules to one `Claim` without modifying it.
- `load_claims()` is the JSON intake boundary. It reads a top-level JSON array,
  converts each `amount` value to `Decimal`, converts each `documents` value to
  a tuple, and returns a list of `Claim` objects.
- `dreamguard.__init__` exposes `Claim`, `ClaimDecision`, `assess_claim()`, and
  `load_claims()` as the package's public API.

## Claims decision rules

Rules are applied in this order to assess each claim:

1. **Claim type validation**: If the claim type is not `"life"` or `"disability"`,
   returns `"rejected"` status with the reason 
   `"Unsupported claim type: <claim_type>"`.

2. **Amount validation**: If the amount is not greater than zero, returns 
   `"rejected"` status with the reason `"Claim amount must be greater than zero"`.

3. **Waiting period check**: If `months_active` is below `3`, returns `"referred"` 
   status with the reason `"Waiting period review required"` and an approved 
   amount of `0`.

4. **Document validation**: For a claim outside the waiting period:
   - A `"life"` claim requires `"death_certificate"` and `"identity_document"`
   - A `"disability"` claim requires `"medical_report"` and `"identity_document"`
   
   If any required documents are missing, returns `"pending_documents"` status 
   with an approved amount of `0`. Reasons are sorted alphabetically by document 
   identifier and use the form `"Missing <document>"`.

5. **Approval**: Any claim that passes all prior checks returns `"approved"` 
   status with the requested amount and no reasons.

## Decision statuses

The `assess_claim()` function returns one of the following statuses:

- `"approved"`: Claim passed all validation checks and is approved for the
  requested amount.
- `"rejected"`: Claim failed type or amount validation. Check reasons for details.
- `"referred"`: Claim passed validation but is in the waiting period
  (`months_active < 3`). Manual review required.
- `"pending_documents"`: Claim is missing required documents for its type.
  Load missing documents and resubmit.

## Validated fields

The current implementation validates the following:

- **Claim type**: Must be `"life"` or `"disability"` (other types rejected)
- **Claim amount**: Must be greater than `0` (zero or negative amounts rejected)
- **Policy active duration** (`months_active`): Checked against 3-month waiting period
- **Required documents**: Checked by claim type (life vs. disability)

The code does not validate policy numbers, document names, or overall JSON shape
beyond what the Python `Claim` dataclass requires.

## Data models

### Claim

Immutable input model for a submitted insurance claim:

```python
@dataclass(frozen=True)
class Claim:
    policy_number: str           # Unique synthetic policy identifier
    claim_type: str              # "life" or "disability"
    amount: Decimal              # Requested amount (use Decimal, not float)
    months_active: int           # Duration policy has been active
    documents: tuple[str, ...]   # Immutable tuple of document identifiers
```

### ClaimDecision

Immutable output model for a claim assessment decision:

```python
@dataclass(frozen=True)
class ClaimDecision:
    status: str              # "approved", "rejected", "referred", or "pending_documents"
    approved_amount: Decimal # Approved amount (0 for non-approved claims)
    reasons: tuple[str, ...] # Immutable tuple of explanatory reasons
```

## JSON format

The `load_claims()` function reads a JSON array of claim records. Each record
must contain:

```json
[
  {
    "policy_number": "SYN-1001",
    "claim_type": "life",
    "amount": "250000.00",
    "months_active": 24,
    "documents": ["death_certificate", "identity_document"]
  },
  {
    "policy_number": "SYN-1002",
    "claim_type": "disability",
    "amount": "80000.00",
    "months_active": 18,
    "documents": ["medical_report", "identity_document"]
  }
]
```

**Important**: The `amount` field must be a string in the JSON; `load_claims()` 
converts it to `Decimal` automatically.

## Usage examples

### Assessing a single claim

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="POL-2024-001",
    claim_type="life",
    amount=Decimal("100000.00"),
    months_active=12,
    documents=("death_certificate", "identity_document")
)

decision = assess_claim(claim)
print(f"Status: {decision.status}")
print(f"Amount: {decision.approved_amount}")
print(f"Reasons: {decision.reasons}")
# Output:
# Status: approved
# Amount: 100000.00
# Reasons: ()
```

### Loading claims from JSON

```python
from dreamguard import load_claims, assess_claim

claims = load_claims("data/sample_claims.json")

for claim in claims:
    decision = assess_claim(claim)
    print(f"{claim.policy_number}: {decision.status}")
```

## Running the tests

From the repository root, run:

```powershell
python -m unittest discover -s tests -v
python scripts/score.py
```

The starter test suite verifies approval of a complete life claim and loading
of the synthetic sample file. The scorecard reports progress across the four
challenge stages; a low score is expected before participants complete them.