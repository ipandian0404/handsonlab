# DreamGuard Copilot Instructions

## Project Context

**DreamGuard Claims** is a training service demonstrating deterministic insurance claim assessment. It converts claim records into assessment decisions using immutable data models and pure decision logic.

**Not production software**: This is a hands-on lab for engineers to practice documentation, testing, and GitHub Copilot workflows. It does not communicate with customers or external systems.

**Public API** (exposed in `dreamguard.__init__`):
- `Claim`: Immutable input model
- `ClaimDecision`: Immutable output model
- `assess_claim(claim: Claim) -> ClaimDecision`: Core decision logic
- `load_claims(path: str | Path) -> list[Claim]`: JSON intake boundary

## Coding Standards

### Naming Conventions (PEP 8)
- **Functions**: lowercase with underscores (`assess_claim`, `load_claims`)
- **Classes**: CapWords (`Claim`, `ClaimDecision`)
- **Constants**: UPPER_CASE with underscores
- **Private**: Leading underscore for module-internal symbols (`_helper_function`)
- **Descriptive**: Use full words; avoid single letters except loop indices (`i`, `j`) and mathematical conventions (`n`, `x`)

### Type Hints (Required)
- All function parameters must have type annotations
- All function return types must be annotated
- Use `from __future__ import annotations` for forward references
- Prefer built-in generics (`list[T]`, `dict[K, V]`, `tuple[T, ...]`)
- Use `str | Path` for file paths accepting both strings and pathlib objects

Example:
```python
def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a claim and return a decision."""
```

### Money Values (Decimal)
- **Always** use `decimal.Decimal` for monetary amounts
- Never use `float` for money (precision issues)
- Import: `from decimal import Decimal`
- Conversion from JSON: `Decimal(record["amount"])` (handles string or numeric input)
- Operations: Arithmetic preserves Decimal type

Example:
```python
amount: Decimal
approved_amount: Decimal("0")
result_amount = claim.amount
```

### Immutability
- Use `@dataclass(frozen=True)` for data models
- Immutable classes cannot be modified after creation
- Tuples for ordered immutable collections (`documents: tuple[str, ...]`)
- Benefits: thread-safe, hashable, clear intent

### Module Docstrings
Every module must have a module-level docstring explaining its purpose and noting that all data is synthetic:

```python
"""Load synthetic claims submitted to the DreamGuard assessment service.

All records in this module are synthetic and for training purposes only.
"""
```

## Testing Requirements

### unittest Framework
- Use Python's built-in `unittest` module
- Location: `tests/` directory
- Naming: `test_*.py` files with `Test*` classes
- Execution: `python -m unittest discover -s tests -v`

### Descriptive Test Names
- Test names should **clearly explain what is being tested** and the expected outcome
- Format: `test_<subject>_<condition>_<expected_result>` where applicable
- Avoid cryptic abbreviations

Good:
```python
def test_assess_claim_approved_when_all_documents_provided(self):
    """A complete claim with all required documents returns approved."""

def test_assess_claim_referred_when_months_active_below_threshold(self):
    """A claim with less than 3 months active is referred for review."""

def test_load_claims_parses_decimal_amount_from_json(self):
    """JSON amount strings are converted to Decimal precision."""
```

Bad:
```python
def test_ok(self):  # Unclear what is being tested
def test_doc_check(self):  # Vague abbreviations
def test_1(self):  # No description
```

### Test Structure
- Use `setUp()` to initialize common test data
- Use descriptive variable names in tests (not `x`, `y`, `r`)
- Include docstrings on test methods explaining the scenario
- Assertions should have clear messages: `self.assertEqual(result, expected, "message")`

Example:
```python
def setUp(self):
    """Create test fixtures."""
    self.valid_life_claim = Claim(
        policy_number="POL-001",
        claim_type="life",
        amount=Decimal("100000"),
        months_active=12,
        documents=("death_certificate", "identity_document")
    )

def test_assess_claim_approved_when_complete_life_claim(self):
    """A life claim with all required documents is approved."""
    decision = assess_claim(self.valid_life_claim)
    self.assertEqual(decision.status, "approved", 
                     "Complete life claim should be approved")
    self.assertEqual(decision.approved_amount, Decimal("100000"),
                     "Approved amount should match requested amount")
```

## Data Policy

### Synthetic Data Only
- **Every record** in this repository must be synthetic (fictional)
- No real customer data, identity information, health records, policy numbers, or financial information
- Synthetic examples: `POL-12345`, `death_certificate`, `medical_report`
- If data looks realistic (real names, SSNs, addresses, account numbers), **reject it immediately**

### Load and Validate
- `load_claims()` reads JSON without validation—validation happens in `assess_claim()`
- Test data in `data/sample_claims.json` must be entirely fictional
- Challenge participants to add only synthetic test cases

## Code Changes

### Focused Changes
- **One concern per commit**: Fix a bug, add a feature, or improve docs—not all at once
- **Minimal scope**: Only modify what's necessary to achieve the change
- **Preserve existing behavior**: Refactoring should not change public API output

### Public API Preservation
- Do **not** rename or remove: `Claim`, `ClaimDecision`, `assess_claim`, `load_claims`
- Do **not** change function signatures (parameters, return types)
- Do **not** change the meaning of status values: `"approved"`, `"referred"`, `"pending_documents"`
- Extensions (new rules, new fields) must be backward compatible or versioned

Example of safe changes:
- Add new validation rules inside `assess_claim` (expands functionality)
- Add optional parameters with defaults (backward compatible)
- Add new public functions (additive, not breaking)

Example of unsafe changes:
- Rename `assess_claim` to `assess` (breaks API)
- Change `Claim.amount` from `Decimal` to `float` (breaks type contract)
- Modify reason format from `"Missing <doc>"` to `"Missing document: <doc>"` (breaks parsing)

### Documentation
- Update docstrings when behavior changes
- Update SERVICE.md to reflect implemented (not planned) rules
- Include docstrings on all public APIs and modules
- Explain why, not just what

## Decision Logic (Current Implementation)

The `assess_claim` function implements these rules in order:

1. **Waiting period**: `months_active` < 3 → status `"referred"`
2. **Required documents**: Missing required docs → status `"pending_documents"`
3. **Approval**: Otherwise → status `"approved"`

**Not yet implemented** (but may be added in challenges):
- Claim type validation (currently accepts any string)
- Amount validation (currently accepts any Decimal)
- Policy number format validation

See [SERVICE.md](../../docs/SERVICE.md) for full decision rules.

## Workflow with Copilot

When asking Copilot to help with DreamGuard:

1. **Be specific**: "Add a test for disability claims missing medical_report" (not just "add a test")
2. **Reference standards**: "Use Decimal for the amount as per project standards"
3. **Preserve API**: "Extend assess_claim without changing its signature"
4. **Synthetic data**: "Use fictional policy numbers like POL-12345"
5. **Review changes**: Always verify that focused changes don't have side effects

Example good prompt:
> Add a test case `test_assess_claim_pending_when_disability_missing_medical_report` that verifies a disability claim without a medical_report returns status pending_documents with appropriate reasons.

## Quick Reference

| Standard | Rule |
|----------|------|
| **Naming** | PEP 8: lowercase functions, CapWords classes |
| **Types** | Required on all functions and module docstrings |
| **Money** | `Decimal` always; never `float` |
| **Testing** | `unittest`, descriptive test names, synthetic data |
| **API** | Preserve existing public API; document changes |
| **Data** | Synthetic only; no real customer information |
| **Changes** | Focused; one concern per commit |
| **Docs** | Module docstrings, function docstrings, synthetic data note |

## Resources

- [SERVICE.md](../../docs/SERVICE.md): Service architecture and decision rules
- [claims.py](../../src/dreamguard/claims.py): Core models and logic
- [intake.py](../../src/dreamguard/intake.py): JSON loading
- [tests/](../../tests/): Test suite with examples
- [README.md](../../README.md): Setup and challenge overview
