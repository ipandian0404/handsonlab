# DreamGuard Claims Service

## Purpose

DreamGuard Claims is a lightweight Python training service that converts synthetic claim records into deterministic assessment results. It is designed for learning, testing, and documentation exercises rather than production claims adjudication. The service does not communicate with customers or external systems.

> All records, claim details, policy numbers, amounts, and document names in this repository are synthetic. Do not add or use real customer, identity, health, policy, contact, or financial data.

## System architecture

The service is intentionally small and composed of a few clear layers.

### 1. Package entry point

File: `src/dreamguard/__init__.py`

This module re-exports the public API:

- `Claim`
- `ClaimDecision`
- `assess_claim`
- `load_claims`

This allows callers to import the service directly with:

```python
from dreamguard import Claim, ClaimDecision, assess_claim, load_claims
```

### 2. Domain models

File: `src/dreamguard/claims.py`

The core types are frozen dataclasses:

- `Claim`: input record for a single claim
- `ClaimDecision`: output record returned by evaluation

`Claim` holds:

- `policy_number: str`
- `claim_type: str`
- `amount: Decimal`
- `months_active: int`
- `documents: tuple[str, ...]`

`ClaimDecision` holds:

- `status: str`
- `approved_amount: Decimal`
- `reasons: tuple[str, ...]`

These models are immutable and are passed between the intake and assessment layers.

### 3. Assessment logic

File: `src/dreamguard/claims.py`

The function `assess_claim(claim: Claim) -> ClaimDecision` evaluates a single claim and returns a `ClaimDecision` without mutating the input object.

The decision flow is:

1. If `months_active < 3`, return `referred` with amount `0` and the reason `Waiting period review required`.
2. Otherwise, compare the required document set for the claim type with the document tuple already attached to the claim.
3. If one or more required documents are missing, return `pending_documents` with amount `0` and one `Missing <document>` reason per missing item.
4. If the waiting-period rule does not trigger and no required documents are missing, return `approved` with the original claim amount and no reasons.

### 4. JSON intake boundary

File: `src/dreamguard/intake.py`

The function `load_claims(path: str | Path) -> list[Claim]` reads a JSON file, expects a top-level array of records, converts each `amount` field to `Decimal`, converts each `documents` list to a tuple, and returns a list of `Claim` objects.

This is the repository’s input boundary for loading claim data from disk.

### 5. Web service entry point

File: `app.py`

The app exposes a tiny HTTP service that serves static challenge files and a simple `/api/assess` endpoint. The endpoint accepts a JSON claim payload, converts it into a `Claim`, calls `assess_claim`, and returns a JSON response with:

- `status`
- `approved_amount`
- `reasons`

This service is used for the browser-based demo and challenge flow.

## Repository structure

```text
.
├── app.py                         # Simple HTTP app and API endpoint
├── azure.yaml                    # Azure deployment config
├── CHALLENGES.md                 # Detailed challenge instructions
├── README.md                     # Lab overview and quick-start instructions
├── pyproject.toml                # Python package metadata
├── data/
│   └── sample_claims.json        # Synthetic sample claim records
├── demo/
│   └── index.html                # Demo UI for claim assessment
├── challenge/
│   └── index.html                # Challenge experience and guide
├── docs/
│   └── SERVICE.md                # Service documentation
├── infra/
│   └── main.bicep                # Azure infrastructure definition
├── scripts/
│   └── score.py                  # Scorecard utility
├── specs/
│   └── claims-status-notifications/
├── src/
│   └── dreamguard/
│       ├── __init__.py           # Public package exports
│       ├── claims.py             # Domain models + assessment rules
│       └── intake.py             # JSON loading for claim records
├── tests/
│   ├── test_app.py               # API and payload validation tests
│   └── test_claims.py            # Claim logic and intake tests
└── .venv/                        # Optional local virtual environment
```

## Setup and running instructions

The following steps are enough for a new developer to set up the project and run the service locally using only this file.

### 1. Open the repository root

```powershell
cd /path/to/handsonlab
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the package in editable mode

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

### 4. Run the test suite

```powershell
python -m unittest discover -s tests -v
```

This executes the repository’s unit tests and validates the core assessment flow and sample claim loading.

### 5. Run the scorecard

```powershell
python scripts/score.py
```

This reports challenge progress and current status across the lab stages.

### 6. Start the local service

```powershell
python app.py
```

The app starts a local web server. The challenge UI is served at:

- http://localhost:8000/challenge/
- http://localhost:8000/demo/

### 7. Validate the API directly

A `POST` to `/api/assess` accepts a JSON payload shaped like a claim object and returns a decision payload.

Example payload:

```json
{
  "policy_number": "SYN-1001",
  "claim_type": "life",
  "amount": "250000.00",
  "months_active": 24,
  "documents": ["death_certificate", "identity_document"]
}
```

Example response:

```json
{
  "status": "approved",
  "approved_amount": "250000.00",
  "reasons": []
}
```

### 8. Load claims from the sample file

```python
from pathlib import Path
from dreamguard import load_claims

claims = load_claims(Path("data/sample_claims.json"))
print(claims)
```

### 9. Evaluate a single claim directly

```python
from decimal import Decimal
from dreamguard import Claim, assess_claim

claim = Claim(
    policy_number="SYN-1001",
    claim_type="life",
    amount=Decimal("250000.00"),
    months_active=24,
    documents=("death_certificate", "identity_document"),
)

result = assess_claim(claim)
print(result)
```

## Business rules implemented in code

The current implementation enforces a small set of rules that are explicitly coded in `assess_claim`.

### Rule 1: waiting period review

If `claim.months_active < 3`, the service returns:

- `status`: `referred`
- `approved_amount`: `Decimal("0")`
- `reasons`: `("Waiting period review required",)`

### Rule 2: required documents by claim type

The service checks required documents using the following map:

- `life`: `death_certificate`, `identity_document`
- `disability`: `medical_report`, `identity_document`

If any required document is missing, the service returns:

- `status`: `pending_documents`
- `approved_amount`: `Decimal("0")`
- `reasons`: one tuple entry per missing document, formatted as `Missing <document>`, sorted by document identifier

### Rule 3: approved outcome

If the claim passes the waiting period rule and all required documents are present, the service returns:

- `status`: `approved`
- `approved_amount`: the original recognized claim amount
- `reasons`: `()`

### Scope boundaries

The current code does not implement additional validation rules such as:

- rejecting unsupported claim types
- rejecting non-positive or zero amounts
- validating policy numbers beyond storing the raw value
- validating JSON shape beyond the keys accessed when loading a record

Those behaviors are not part of the implemented logic in the current codebase.

## Data and privacy

All records in this repository are synthetic. Only fictional policy numbers,
claim details, documents, and monetary values should be used in examples,
tests, and exercises. Do not add real customer, identity, health, policy,
contact, or financial information to this project.

## Summary

DreamGuard Claims is a small training service that loads synthetic claims, evaluates a narrow decision flow, and returns an immutable `ClaimDecision` object. New developers can run the unit tests, run the scorecard, and start the local service with the commands in this guide. The code intentionally models a simplified claims-approval workflow, and the behavior described here matches the current implementation.
