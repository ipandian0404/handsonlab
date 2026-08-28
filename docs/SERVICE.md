# DreamGuard Claims Service

## Purpose

DreamGuard Claims is a training service that converts fictional claim records
into deterministic assessment decisions. It reads synthetic claims via JSON,
applies a fixed set of decision rules, and produces outcome decisions with
explanatory reasons. Engineers can use this service to practice documentation,
testing, and GitHub Copilot workflows. It is not a production claims processor
and does not communicate with customers or external systems.

## Scope and limitations

- DreamGuard assesses only the claim record contents; it does not validate
  policy numbers, document names, or JSON structure.
- Assessment is deterministic: identical claims always produce identical
  decisions.
- The service is read-only; it does not modify input claims, store state, or
  trigger side effects.
- All records in the repository and any extended dataset must be fictional.
  Every policy number, claim detail, document identifier, and monetary value
  is synthetic for training purposes only.

## Public API

The DreamGuard package exposes four public symbols:

### `Claim`

An immutable dataclass representing a synthetic claim submitted for assessment.

**Fields:**
- `policy_number` (str): Fictional identifier for the policy. Not validated.
- `claim_type` (str): The claim type, such as `"life"` or `"disability"`.
  Only these two types are supported; others trigger rejection.
- `amount` (Decimal): The claimed amount. Must be greater than zero.
- `months_active` (int): How long the policy has been active, in months.
  Claims from policies active fewer than three months are referred.
- `documents` (tuple[str, ...]): Immutable tuple of fictional document
  identifiers, such as `"death_certificate"` or `"identity_document"`.

**Example:**
```python
from decimal import Decimal
from dreamguard import Claim

claim = Claim(
    policy_number="POL-2025-001",
    claim_type="life",
    amount=Decimal("50000.00"),
    months_active=24,
    documents=("death_certificate", "identity_document"),
)
```

### `ClaimDecision`

An immutable dataclass representing the outcome of assessing a synthetic claim.

**Fields:**
- `status` (str): The assessment outcome. Possible values are:
  - `"approved"`: Claim meets all requirements.
  - `"rejected"`: Claim violates policy constraints (unsupported type, invalid
    amount).
  - `"referred"`: Claim requires manual review due to the policy waiting period.
  - `"pending_documents"`: Required documents are missing.
- `approved_amount` (Decimal): The amount approved by assessment. Zero for
  non-approved outcomes; equal to the requested amount for approved claims.
- `reasons` (tuple[str, ...]): Immutable tuple of explanatory strings.
  Empty for approved claims. Strings are sorted lexicographically.

**Example:**
```python
from dreamguard import ClaimDecision
from decimal import Decimal

decision = ClaimDecision(
    status="approved",
    approved_amount=Decimal("50000.00"),
    reasons=(),
)
```

### `assess_claim(claim: Claim) -> ClaimDecision`

Assesses a synthetic claim and produces a deterministic decision.

Applies assessment rules in a fixed sequence (see the [Claims decision rules](#claims-decision-rules)
section). Assessment is stateless and does not modify the input claim.

**Arguments:**
- `claim`: The Claim object to assess.

**Returns:**
- A ClaimDecision with the status, approved amount, and reasons.

**Example:**
```python
from dreamguard import Claim, assess_claim
from decimal import Decimal

claim = Claim(
    policy_number="POL-2025-001",
    claim_type="life",
    amount=Decimal("50000.00"),
    months_active=24,
    documents=("death_certificate", "identity_document"),
)

decision = assess_claim(claim)
print(decision.status)  # "approved"
print(decision.approved_amount)  # Decimal('50000.00')
```

### `build_notification_message(claim: Claim, decision: ClaimDecision) -> str`

Builds a simple human-readable notification for the outcome of a claim assessment.
The helper uses the current decision status and returns a deterministic message
for the supported states: approved, rejected, referred, and pending_documents.

**Arguments:**
- `claim`: The Claim object that was assessed.
- `decision`: The ClaimDecision produced by `assess_claim()`.

**Returns:**
- A descriptive notification string for the supplied decision.

**Example:**
```python
from dreamguard import Claim, assess_claim, build_notification_message
from decimal import Decimal

claim = Claim(
    policy_number="POL-2025-001",
    claim_type="life",
    amount=Decimal("50000.00"),
    months_active=24,
    documents=("death_certificate", "identity_document"),
)

decision = assess_claim(claim)
message = build_notification_message(claim, decision)
print(message)
```

### `load_claims(path: str | Path) -> list[Claim]`

Loads synthetic claims from a JSON file and converts them to Claim objects.

Reads a JSON file containing a top-level array of claim records. Each record
must have `policy_number`, `claim_type`, `amount`, `months_active`, and
`documents` fields. The `amount` is converted to `Decimal`, and `documents`
is converted to a tuple. File shape is not validated.

**Arguments:**
- `path`: Path to a JSON file (str or Path object).

**Returns:**
- A list of Claim objects.

**Raises:**
- `FileNotFoundError`: File does not exist.
- `json.JSONDecodeError`: File is not valid JSON.
- `KeyError`: A record is missing a required field.
- `ValueError`: The `amount` field cannot be converted to Decimal.

**Example:**
```python
from dreamguard import load_claims

claims = load_claims("data/sample_claims.json")
for claim in claims:
    print(f"Policy {claim.policy_number}: {claim.amount}")
```

## Claims decision rules

Assessment rules are applied in this fixed order. The first matching rule
determines the decision:

1. **Unsupported claim type:** If `claim_type` is not `"life"` or
   `"disability"`, return:
   - Status: `"rejected"`
   - Approved amount: `Decimal("0")`
   - Reason: `"Unsupported claim type: <claim_type>"`

2. **Invalid amount:** If `amount` is zero or negative, return:
   - Status: `"rejected"`
   - Approved amount: `Decimal("0")`
   - Reason: `"Claim amount must be greater than zero"`

3. **Waiting period:** If `months_active` is less than `3`, return:
   - Status: `"referred"`
   - Approved amount: `Decimal("0")`
   - Reason: `"Waiting period review required"`

4. **Missing documents:** Check that all required documents are present:
   - `"life"` claims require: `"death_certificate"` and `"identity_document"`
   - `"disability"` claims require: `"medical_report"` and
     `"identity_document"`
   
   If any required documents are missing, return:
   - Status: `"pending_documents"`
   - Approved amount: `Decimal("0")`
   - Reasons: Sorted list of strings like `"Missing death_certificate"`

5. **Approval:** If all rules above pass, return:
   - Status: `"approved"`
   - Approved amount: The full requested amount
   - Reasons: Empty tuple

**Validation scope:** The code validates only claim type, amount, and required
documents. It does not validate policy numbers, active-policy duration,
document names, or JSON structure.

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