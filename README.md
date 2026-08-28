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

## Facilitator notes

The starter branch is intentionally incomplete. A low initial score is expected;
the two baseline tests should still pass. Participants may ask Copilot to explain
code and propose changes, but they remain responsible for reviewing every result.