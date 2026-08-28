# DreamGuard Copilot Instructions

## Project Context

**DreamGuard** is a training service demonstrating claims assessment logic. It converts insurance claim records into deterministic decisions using immutable data models and pure functions.

- **Purpose**: Educational tool for documentation, testing, and GitHub Copilot workflows
- **Not production**: Does not communicate with customers or external systems
- **Data**: All records are synthetic; no real customer, health, or financial information may be added

## Core Architecture

### Public API
The public API is exposed by `dreamguard.__init__`:
- `Claim`: Immutable input model with `policy_number`, `claim_type`, `amount` (Decimal), `months_active`, `documents` (tuple)
- `ClaimDecision`: Immutable output model with `status`, `approved_amount` (Decimal), `reasons` (tuple)
- `assess_claim(claim: Claim) -> ClaimDecision`: Pure function applying decision rules
- `load_claims(path: str | Path) -> list[Claim]`: JSON intake boundary

**Preserve the public API contract:** Do not remove, rename, or change the signature of exported symbols.

### Implemented Decision Rules
The `assess_claim()` function applies these rules (in order):
1. Claims with `months_active < 3` return `"referred"` status (waiting period)
2. Missing required documents (by claim type) return `"pending_documents"` status
3. Eligible claims return `"approved"` with the requested amount

Unsupported: Claim type validation, amount validation, policy number validation, JSON shape validation.

## Coding Standards

### Naming
- Follow **PEP 8** for all identifiers: snake_case for functions/variables, PascalCase for classes
- Use descriptive, intent-revealing names
- Avoid abbreviations except where conventional (e.g., `Decimal`)

### Type Hints
- **Require type hints on all public functions** (exported in `__init__`)
- Use type hints on internal functions where they improve clarity
- Use `Decimal` for monetary amounts, never `float`
- Indicate immutable collections: `tuple[str, ...]` for immutable sequences

### Data Models
- Immutable dataclasses with `frozen=True` for input/output models
- Immutable tuples for collections of document identifiers and decision reasons
- No mutable state in public APIs

### Monetary Values
- Use `from decimal import Decimal` for all monetary amounts
- Convert JSON amounts to `Decimal` during intake (`load_claims`)
- Return `Decimal` in `ClaimDecision.approved_amount`
- Never use `float` for money

## Testing

### Test Organization
- Place tests in `tests/` directory
- Name test files `test_*.py` following standard unittest conventions
- Run tests: `python -m unittest discover -s tests -v`

### Test Quality
- Use descriptive test method names that document behavior: `test_<function>_<scenario>_<expected_result>`
  - ✅ Good: `test_assess_claim_waiting_period_returns_referred`
  - ❌ Bad: `test_claim()` or `test_1()`
- One logical assertion per test; use multiple tests for multiple scenarios
- Test only public API; do not test private implementation details
- Use synthetic data only (see Data below)

## Data Requirements

### Synthetic Data Only
- Every test fixture, sample file, and example must use **fictional data only**
- No real customer information, identity data, health records, policy numbers, addresses, or financial information
- Valid fiction: Made-up policy numbers (e.g., `POL-2024-001`), claim amounts, document names, names

### Sample Data
- Store synthetic test data in `data/sample_claims.json` and similar locations
- Use consistent fictional scenarios (e.g., "Jane Doe", "John Smith" with clearly fictional details)

## Code Changes

### Focus and Scope
- Make **focused, atomic changes** that address a single concern
- Avoid refactoring unrelated code in the same change
- Document the intent of changes in commit messages and docstrings

### Preservation Rules
- **Do not modify the public API contract** without explicit approval
  - No renaming exported functions or classes
  - No changing function signatures in the public API
  - No removing `__all__` exports
- **Do not remove or alter implemented decision rules** without explicit approval
- Extending functionality (new rules, new tests) is welcome

### Documentation
- Add or update docstrings for public functions (module, class, function level)
- Document synthetic data constraints in module docstrings
- Update `docs/SERVICE.md` when decision rules or public API change
- Use Google-style or NumPy-style docstrings with clear Args, Returns, Raises sections

## Development Workflow

### Before making changes:
1. Understand the current public API in `src/dreamguard/__init__`
2. Read decision rules in `docs/SERVICE.md`
3. Run tests: `python -m unittest discover -s tests -v`
4. Check scorecard: `python scripts/score.py`

### Example: Adding a new test
```python
def test_assess_claim_complete_disability_claim_approved(self):
    """A disability claim with all required documents is approved."""
    claim = Claim(
        policy_number="POL-2024-001",
        claim_type="disability",
        amount=Decimal("5000.00"),
        months_active=12,
        documents=("medical_report", "identity_document")
    )
    decision = assess_claim(claim)
    self.assertEqual(decision.status, "approved")
    self.assertEqual(decision.approved_amount, Decimal("5000.00"))
    self.assertEqual(decision.reasons, ())
```

### Example: Adding a docstring
```python
def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a claim and return a decision without modifying the claim.
    
    Applies decision rules in order: waiting period check, document validation,
    and approval. All records assessed are synthetic.
    
    Args:
        claim: A Claim object to assess.
    
    Returns:
        A ClaimDecision with status, approved_amount, and reasons.
    """
```

## Quick Reference

| Aspect | Rule |
|--------|------|
| Money | Use `Decimal`, never `float` |
| Data | Synthetic only, no real information |
| API | Preserve public contract; no removal or renaming |
| Tests | Descriptive names; test public API only |
| Naming | PEP 8: snake_case functions, PascalCase classes |
| Type Hints | Required on public functions; use `tuple` for immutable sequences |
| Focus | One concern per change; avoid unrelated refactoring |
