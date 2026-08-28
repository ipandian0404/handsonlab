# DreamGuard Repository Instructions

## Project context

DreamGuard is a Python 3.10+ training package for assessing fictional insurance
claims. Source code lives under `src/dreamguard`, tests use the standard-library
`unittest` framework, and `scripts/score.py` measures challenge progress.

- Keep claim domain models and assessment rules in `src/dreamguard/claims.py`.
- Keep JSON loading and conversion at the intake boundary in
  `src/dreamguard/intake.py`.
- Treat exports from `src/dreamguard/__init__.py` as the public API.
- Keep the runtime dependency-free unless a requirement clearly justifies a
  new package.

## Python standards

- Follow PEP 8 naming and formatting conventions.
- Add accurate type hints to new and changed functions, methods, and public
  attributes.
- Use descriptive names; avoid unexplained abbreviations and one-letter names.
- Use `Decimal` for money. Do not represent monetary values with `float`.
- Prefer immutable domain values where practical and keep assessment behavior
  deterministic.
- Add concise docstrings to public APIs. Document only behavior supported by
  the implementation and avoid comments that merely restate code.

## Testing

- Use `unittest`; do not introduce another test framework.
- Give tests descriptive names such as
  `test_life_claim_with_missing_identity_document_is_pending`.
- Add focused tests for each changed rule, including boundary and invalid-input
  cases where relevant.
- Run `python -m unittest discover -s tests -v` after code changes.
- Run `python scripts/score.py` when completing a challenge stage.

## Data and privacy

- Use synthetic data only. Every claim, policy number, identity, document,
  contact detail, health detail, and monetary value must be fictional.
- Never add real customer, policy, identity, health, contact, or financial data
  to source, tests, fixtures, documentation, prompts, logs, or examples.
- Make the synthetic nature of records explicit in user-facing documentation.

## Change discipline

- Keep changes focused on the requested behavior and avoid unrelated refactors.
- Preserve the public API unless the request explicitly requires a breaking
  change. Do not rename or remove public exports without updating callers,
  tests, and documentation.
- Maintain existing behavior unless a requested change and its tests define a
  new contract.
- Review generated code for correctness, privacy, and consistency before
  accepting it.