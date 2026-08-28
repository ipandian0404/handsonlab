# Momentum Financial Dreams Copilot Enterprise Challenge Race

Use GitHub Copilot to turn a small, fictional insurance-claims service into
production-ready software. The scenario is inspired by Momentum Group's public
purpose of building and protecting clients' financial dreams.

> [!IMPORTANT]
> This independent training exercise is not affiliated with or endorsed by
> Momentum Group. DreamGuard, policy numbers, rules, and claim records are
> fictional. Never use real customer, policy, health, or identity data in this lab.

## The race

| Stage | Engineering pillar | Points |
| --- | --- | ---: |
| 1 | Documentation | 25 |
| 2 | Custom instructions | 25 |
| 3 | Spec-driven development agent | 25 |
| 4 | Testing | 25 |
| 5 | Build and demo | Completion step |
| 6 | GitLab MCP | Completion step |

Start with [the interactive race guide](challenge/index.html), then use
[the detailed challenge brief](CHALLENGES.md) while working in VS Code.

## Prerequisites

- Git
- Python 3.10 or newer
- Visual Studio Code
- GitHub Copilot and GitHub Copilot Chat
- Edge or Chrome

No third-party Python packages are required.

## Quick start

```powershell
git switch -c <your-initials-and-surname>
python -m unittest discover -s tests -v
python scripts/score.py
python app.py
```

Open <http://localhost:8000/challenge/> for the race guide. Complete the stages
in order, rerun the tests and scorecard, and commit after each stage.

## Build and run the project

DreamGuard is a dependency-free Python package with a static HTML frontend.
Optionally create an isolated environment, install the package, and validate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m compileall -q src scripts tests
python -m unittest discover -s tests -v
python scripts/score.py
```

Start the frontend in a separate terminal:

```powershell
python app.py
```

Open <http://localhost:8000/challenge/> for the guide and
<http://localhost:8000/demo/> for the live Claims Workbench. The workbench sends
synthetic claim inputs to the Python assessment API, so changes to
`assess_claim` are visible in the browser. No npm installation or frontend
compilation is required. Stop the server with `Ctrl+C`.

## GitLab MCP

The sixth challenge step connects GitHub Copilot in VS Code to GitLab's hosted
MCP server. It uses HTTP transport and browser-based OAuth; do not paste tokens
into chat or commit credentials. GitLab currently marks this feature as Beta and
an administrator must enable the required GitLab Duo, beta-feature, and MCP
access settings.

When VS Code asks for the server ID, type `GitLab`. This is a local display name
you choose, not an identifier that must be copied from GitLab.

See [the GitLab MCP challenge](CHALLENGES.md#6-gitlab-mcp)
and the [official GitLab MCP server documentation](https://docs.gitlab.com/user/model_context_protocol/mcp_server/).

## Deploy to Azure App Service

The repository includes an `azd` configuration and Bicep infrastructure for a
Linux Azure Web App. After signing in to Azure Developer CLI, deploy with:

```powershell
azd auth login
azd env new momentum-race
azd env set AZURE_LOCATION southafricanorth
azd provision --preview
azd up
```

The deployment creates a B1 App Service plan, Web App, Application Insights,
and Log Analytics workspace. Set a different `AZURE_LOCATION` or select another
allowed `appServicePlanSku` in [infra/main.bicep](infra/main.bicep) when needed.

## Project map

```text
challenge/             Interactive participant guide
demo/                  Live claims assessment workbench
data/                  Synthetic claim records
docs/SERVICE.md        Documentation challenge target
scripts/score.py       Local scorecard
src/dreamguard/        Claims assessment starter service
tests/                 Starter unit tests
CHALLENGES.md          Detailed tasks and acceptance criteria
```

## Copilot custom instructions

GitHub Copilot Chat operates within the following guardrails for DreamGuard:

### Project context

**DreamGuard** is a lightweight training service that processes synthetic insurance
claims through deterministic assessment rules. It has no external dependencies,
connects to no live systems, and is never deployed with real data.

Key architecture:
- `Claim`: immutable input dataclass (policy_number, claim_type, amount, months_active, documents)
- `ClaimDecision`: immutable output dataclass (status, approved_amount, reasons)
- `assess_claim(claim)`: applies decision rules deterministically
- `load_claims(json_text)`: parses JSON array into Claim objects
- Public API: exported via `dreamguard/__init__.py`

Decision rules (as implemented):
1. Waiting period: `months_active < 3` → `referred` status
2. Document validation: missing required docs → `pending_documents` status
3. Otherwise: `approved` status with requested amount

### Code style and quality

**Naming conventions:** Follow PEP 8 consistently.
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private/internal methods: prefix with `_`

**Type hints:** All function signatures must include type annotations.
- Use `from __future__ import annotations` for forward references
- Use `Decimal` from decimal module for all monetary amounts
- Use `tuple[str, ...]` for immutable sequences

**Monetary values:** Always use `Decimal` type (not float).
- Import: `from decimal import Decimal`
- Never mix float and Decimal in arithmetic
- Create Decimal instances from strings: `Decimal("100.50")` not `Decimal(100.50)`

**Immutability:** Favor frozen dataclasses and immutable data structures.
- Mark dataclasses with `@dataclass(frozen=True)`
- Use tuples instead of lists for immutable collections
- Minimize mutation of shared state

### Testing

**Testing framework:** unittest (in `tests/` folder).
- Test file naming: `test_*.py` matching module structure
- Test function naming: `test_<function>_<scenario>` (descriptive)
- Use `setUp()` and `tearDown()` for test fixtures
- Each test class tests one module or class
- One assertion per test is preferred; keep tests focused

**Example test name:** `test_assess_claim_referred_when_months_active_below_three`

**Coverage:** Aim for branch coverage on all public API functions.
- Test success paths, error paths, and edge cases
- Test with synthetic data only (fictional amounts, document names, policy numbers)

### Data and privacy

**Synthetic data only:** Every record—test fixtures, sample data, documentation
examples, and test assertions—must be completely fictional.

- Policy numbers: generate or use fictional patterns (no real formats)
- Amounts: use any reasonable fictional Decimal values
- Documents: use placeholder names (`identity_document`, `medical_report`, etc.)
- Claim types: only `life` and `disability` in current scope
- Names and dates: use fictional values

**Never commit:**
- Real customer information or policy numbers
- Actual health or financial data
- Real identity documents or references
- Personal contact information

### Code review principles

**Preserve public API:** Changes to public functions, classes, and exports in
`dreamguard/__init__.py` require explicit API review. Do not rename or remove
public symbols without discussion.

**Focused changes:** Each commit should accomplish one goal.
- Documentation updates separate from code changes
- Refactoring separate from feature additions
- Test additions paired with the code they cover

**Completeness:** Changes must fully address the stated requirement.
- If a function needs type hints, add them to all parameters and return type
- If a test scenario is incomplete, complete it
- If documentation is partial, finish it

**Validation:** After code changes, confirm:
- All existing tests still pass
- New tests pass
- Type hints are complete and correct
- No hard-coded assumptions beyond current scope

## Facilitator notes

The starter branch is intentionally incomplete. A low initial score is expected;
the two baseline tests should still pass. Participants may ask Copilot to explain
code and propose changes, but they remain responsible for reviewing every result.