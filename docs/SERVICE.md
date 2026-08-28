# DreamGuard Claims Service Guide

## Overview

DreamGuard Claims is a lightweight training service for evaluating synthetic claim records. It does not perform customer-facing claims processing and it does not call external systems or services.

The public package surface is defined in `src/dreamguard/__init__.py` and exposes:

- `Claim`
- `ClaimDecision`
- `assess_claim`
- `load_claims`

This service is intentionally narrow: it reads claim records, converts them into domain objects, evaluates a short decision flow, and returns a status result.

## Synthetic data notice

All records, claim details, policy values, documents, and amounts in this repository are synthetic. Do not add or use real customer, identity, health, policy, contact, or financial information in sample data or exercises.

## Setup and running instructions

From the repository root, create and activate a Python environment if needed, then run the project commands below.

### 1. Change to the repository root

```powershell
cd /path/to/handsonlab
```

### 2. Create and activate a virtual environment (optional but recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install project dependencies

```powershell
pip install -r requirements.txt
```

If this repository uses the project metadata in `pyproject.toml`, the package can also be installed in editable mode:

```powershell
pip install -e .
```

### 4. Run the unit tests

```powershell
python -m unittest discover -s tests -v
```

### 5. Run the scorecard

```powershell
python scripts/score.py
```

### 6. Load sample claims manually

The JSON intake path is implemented in `src/dreamguard/intake.py`. The repository includes a sample file at `data/sample_claims.json`.

```python
from pathlib import Path
from dreamguard import load_claims

claims = load_claims(Path("data/sample_claims.json"))
print(claims)
```

### 7. Evaluate a single claim

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="POL-1001",
    claim_type="life",
    amount=Decimal("2500.00"),
    months_active=12,
    documents=("death_certificate", "identity_document"),
)

result = assess_claim(claim)
print(result)
```

## Architecture overview

The service has a simple, layered structure:

### 1. Data intake layer

File: `src/dreamguard/intake.py`

`load_claims(path)`:

- opens a JSON file using `Path(path)`
- reads a top-level JSON array
- iterates through each record
- converts `amount` to `Decimal`
- converts `documents` to a tuple
- builds a `Claim` object for each record

This function is the JSON boundary for the service. It does not validate schema beyond the expected dictionary keys being present when accessed.

### 2. Domain model layer

File: `src/dreamguard/claims.py`

`Claim` is a frozen dataclass representing a single claim input record:

- `policy_number: str`
- `claim_type: str`
- `amount: Decimal`
- `months_active: int`
- `documents: tuple[str, ...]`

`ClaimDecision` is a frozen dataclass representing the service result:

- `status: str`
- `approved_amount: Decimal`
- `reasons: tuple[str, ...]`

These models are immutable and are passed between the intake and assessment layers.

### 3. Decision logic layer

File: `src/dreamguard/claims.py`

`assess_claim(claim: Claim) -> ClaimDecision` applies the implemented decision rules to one claim. It does not mutate the input `Claim` and returns a new `ClaimDecision` object.

The decision flow works like this:

1. Evaluate the waiting-period rule.
2. If the claim has passed the waiting period, check the required documents for the claim type.
3. If any required documents are missing, return `pending_documents`.
4. Otherwise, return `approved`.

### 4. Package API layer

File: `src/dreamguard/__init__.py`

This module re-exports the package's public API so callers can use:

```python
from dreamguard import Claim, ClaimDecision, assess_claim, load_claims
```

## Business and claims rules enforced by the code

The current implementation enforces only the checks that are explicitly coded in `assess_claim`.

### Rule 1: waiting period review

If `claim.months_active < 3`, the service returns:

- status: `referred`
- approved amount: `Decimal("0")`
- reasons: `("Waiting period review required",)`

This is the first rule evaluated.

### Rule 2: document requirement by claim type

After the waiting-period gate, the service checks required documents using this mapping:

- `life` requires: `death_certificate` and `identity_document`
- `disability` requires: `medical_report` and `identity_document`

Any missing documents result in:

- status: `pending_documents`
- approved amount: `Decimal("0")`
- reasons: one entry per missing document in the form `Missing <document>`, sorted by document identifier

### Rule 3: approved outcome

If the claim is not in the waiting period and all required documents are present, the service returns:

- status: `approved`
- approved amount: the original claim amount
- reasons: an empty tuple `()`

## Behaviors not implemented by this code

The service does not currently validate or enforce the following behaviors:

- unsupported claim types are not rejected by rule
- negative or zero amounts are not rejected by rule
- policy numbers are not validated
- document names beyond exact identifier comparison are not validated beyond the required set
- JSON structure beyond the expected dictionary keys is not validated by the library itself

This guide is intentionally limited to behaviors that are actually present in the code.

## Example decision flow

### Example: referred claim

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="POL-2001",
    claim_type="life",
    amount=Decimal("5000.00"),
    months_active=2,
    documents=("death_certificate", "identity_document"),
)

print(assess_claim(claim))
# ClaimDecision(status='referred', approved_amount=Decimal('0'), reasons=('Waiting period review required',))
```

### Example: pending documents

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="POL-2002",
    claim_type="life",
    amount=Decimal("5000.00"),
    months_active=12,
    documents=("identity_document",),
)

print(assess_claim(claim))
# ClaimDecision(status='pending_documents', approved_amount=Decimal('0'), reasons=('Missing death_certificate',))
```

### Example: approved claim

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="POL-2003",
    claim_type="life",
    amount=Decimal("5000.00"),
    months_active=12,
    documents=("death_certificate", "identity_document"),
)

print(assess_claim(claim))
# ClaimDecision(status='approved', approved_amount=Decimal('5000.00'), reasons=())
```

## Summary

The DreamGuard service is a simple synthetic claims assessment example. It reads claim records, converts them to typed objects, applies a short rule set, and returns an immutable decision record without external processing. All data in the repository is synthetic, and the service behavior described here matches the code as it exists today.
