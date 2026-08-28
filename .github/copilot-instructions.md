# DreamGuard Copilot Instructions

## Project Context

**DreamGuard** is a training service for learning Python documentation, testing, and GitHub Copilot workflows. It accepts synthetic insurance claim records, applies deterministic assessment rules, and produces claim decisions.

- **Purpose**: Educational tool; not a production system.
- **Core module**: `dreamguard` package in `src/dreamguard/`
- **Key files**:
  - `src/dreamguard/claims.py` – Assessment rules and data models.
  - `src/dreamguard/intake.py` – JSON claim loading.
  - `src/dreamguard/__init__.py` – Public API exports.
  - `docs/SERVICE.md` – Service documentation.
  - `tests/` – Unit tests using `unittest`.
  - `scripts/score.py` – Challenge scorecard.

## Naming and Code Style

- **PEP 8 compliance required**: Follow [PEP 8](https://pep8.org/) for all Python code.
  - Snake case for variables, functions, and module names.
  - CapWords for classes.
  - UPPER_CASE for constants.
  - Avoid single-letter variable names except in loops (`i`, `j`).

- **Descriptive names**: Names must clearly convey intent.
  - ✓ `assess_claim()`, `required_documents`, `missing_documents`
  - ✗ `check()`, `x`, `temp_var`

- **Type hints required**: All functions and public methods must have type hints for parameters and return types.
  ```python
  def assess_claim(claim: Claim) -> ClaimDecision:
  def load_claims(path: str | Path) -> list[Claim]:
  ```

## Monetary Values

- **Decimal only**: All monetary amounts must use `decimal.Decimal`, never `float`.
  - ✓ `amount: Decimal`, `Decimal("50000.00")`
  - ✗ `amount: float`, `amount = 50000.0`
  - Reason: Preserves precision for financial calculations.

## Testing

- **unittest framework**: Use Python's built-in `unittest` module; do not introduce external test frameworks.

- **Descriptive test names**: Test function names must clearly describe what is being tested.
  - ✓ `test_approved_claim_with_complete_documents`
  - ✓ `test_rejected_when_claim_type_unsupported`
  - ✗ `test_1()`, `test_claim()`, `test_check()`

- **Comprehensive coverage**: Write tests for:
  - Happy path (expected behavior).
  - Edge cases (boundary values like `months_active < 3`, `amount <= 0`).
  - All rejection and referral reasons.
  - All claim types and document combinations.

- **Assertion messages**: Use descriptive assertion messages for failures.
  ```python
  self.assertEqual(decision.status, "approved", 
                   f"Expected status 'approved' for complete life claim")
  ```

## Synthetic Data Only

- **All records must be fictional**:
  - Policy numbers: Use format like `POL-2025-001`, `POL-TRAIN-123`.
  - Claim types: Only `"life"` and `"disability"` (hardcoded in assessment rules).
  - Amounts: Use realistic but synthetic values (e.g., `Decimal("50000.00")`).
  - Document names: Use identifiers like `"death_certificate"`, `"medical_report"`.
  - No real customer, identity, health, policy, contact, or financial data.

- **Validation**: Do not commit files with real data. All sample data files (JSON, CSV, etc.) must contain only synthetic records.

- **Documentation**: Always document that data is synthetic. Example:
  ```python
  def load_claims(path: str | Path) -> list[Claim]:
      """Load synthetic claims from a JSON file and convert to Claim objects."""
  ```

## Focused Changes

- **Single responsibility**: Each code change should address one issue or feature.
  - ✓ "Add type hints to `load_claims()`"
  - ✗ "Refactor claims module, add docstrings, and change exception handling"

- **Minimal scope**: Make only the changes necessary to fulfill the request.
  - Do not reformat unrelated code.
  - Do not restructure modules unnecessarily.
  - Do not optimize unrelated functions.

- **Commit hygiene**: If implementing multiple independent changes, create separate commits or clearly document each in a single commit message.

## Public API Preservation

- **Exports must not break**: The following symbols are part of the public API and must never be removed or have incompatible signature changes:
  - `dreamguard.Claim` – Immutable dataclass with fields: `policy_number`, `claim_type`, `amount`, `months_active`, `documents`.
  - `dreamguard.ClaimDecision` – Immutable dataclass with fields: `status`, `approved_amount`, `reasons`.
  - `dreamguard.assess_claim(claim: Claim) -> ClaimDecision` – Assessment function.
  - `dreamguard.load_claims(path: str | Path) -> list[Claim]` – JSON loader.

- **Signature compatibility**: 
  - Do not change parameter names or types.
  - Do not change return types.
  - New parameters must have defaults to maintain backward compatibility.
  - Do not remove or rename exported symbols.

- **Documentation contracts**: Public API docstrings (including examples in `SERVICE.md`) document the behavioral contract. Changes must not contradict documented behavior.

## Assessment Rules

The following assessment rules are fixed and must not be altered:

1. Unsupported claim types are rejected.
2. Non-positive amounts are rejected.
3. Claims active for fewer than 3 months are referred.
4. Life claims require `death_certificate` and `identity_document`.
5. Disability claims require `medical_report` and `identity_document`.
6. Missing documents result in `pending_documents` status.
7. Claims passing all rules are approved for the requested amount.

Changes to business logic must be proposed through challenge specifications or documentation updates, not through code modifications.

## Documentation

- **Docstrings required**: All public functions and classes must have docstrings.
  - Use the [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for consistency.
  - Include examples for public functions.
  - Document all exceptions that can be raised.

- **SERVICE.md is the source of truth** for API contracts, behavior, and examples. Keep it current when public API behavior changes.

- **Inline comments**: Use sparingly. Let code and docstrings speak first.

## Workflow

1. **Read the specification**: Review `docs/SERVICE.md` and relevant docstrings before writing code.
2. **Write tests first**: When adding features, write tests that describe the desired behavior.
3. **Implement against tests**: Write code to pass tests, not the reverse.
4. **Run the full suite**: Always run `python -m unittest discover -s tests -v` before committing.
5. **Verify the scorecard**: Run `python scripts/score.py` to check progress on challenges.

## Resources

- **Service documentation**: [docs/SERVICE.md](../docs/SERVICE.md)
- **Main module**: [src/dreamguard/claims.py](../src/dreamguard/claims.py)
- **Tests**: [tests/](../tests/)
- **PEP 8 guide**: https://pep8.org/
- **Python Decimal**: https://docs.python.org/3/library/decimal.html
