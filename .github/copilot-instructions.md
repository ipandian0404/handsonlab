# DreamGuard Repository Copilot Instructions

## 1. Project Context & Architecture
- **Domain:** DreamGuard Claims Management System.
- **Architecture:** Modularity centered around `src/dreamguard/claims.py` and modular financial logic.
- **Data Privacy:** ALL data in this repository is strictly **synthetic**. Never insert real personal identifiable information (PII) or real-world financial credentials.

## 2. Python Code Style & Standards
- **PEP 8 Compliance:** Follow PEP 8 guidelines strictly (snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants).
- **Type Hints:** Include explicit type annotations for all function parameters, return values, and class attributes (`from typing import Optional, List, Dict`).
- **Financial & Precision Calculations:** ALWAYS use `decimal.Decimal` for monetary values, currency, rates, or calculations involving money. NEVER use `float` or `int` for monetary amounts.

## 3. Testing Standards
- **Framework:** Use Python's built-in `unittest` library unless otherwise specified.
- **Naming Conventions:** Write highly descriptive test method names that express intent (e.g., `test_claim_approval_raises_value_error_when_amount_exceeds_limit`).
- **Isolation:** Ensure test cases use synthetic fixtures and mock external dependencies where necessary.

## 4. Documentation & Public API Rules
- **Public API Preservation:** Do not break existing public method signatures or return types unless explicitly instructed.
- **Docstrings:** Use Google-style docstrings for all public classes, methods, and functions, detailing `Args`, `Returns`, and `Raises`.
- **Comments:** Include inline comments strictly to explain non-obvious reasoning ("why") rather than self-evident code ("what").