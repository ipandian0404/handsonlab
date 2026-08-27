# Momentum Financial Dreams Copilot Enterprise Challenge Race

Race through four enterprise challenges using GitHub Copilot to improve the
fictional **DreamGuard Claims** service. All records and rules are synthetic.
This independent lab is not affiliated with Momentum Group.

## 1. Documentation

**START**

Great software starts with great documentation. Use Copilot to make DreamGuard
accessible to engineers, reviewers, and risk partners.

### Your Mission

Create meaningful service documentation, public API docstrings, and selective
comments that explain why non-obvious claims decisions are made.

### Enterprise Value

Documentation reduces onboarding time, enables knowledge transfer, and keeps
financial-services software maintainable and reviewable.

### Steps to Complete

1. Create a branch named with your initials and surname, such as `jd-doe`.
2. Complete every section in `docs/SERVICE.md`.
3. Add docstrings to public types and functions in `src/dreamguard/claims.py`.
4. Add concise comments only where reasoning is not evident from the code.
5. Commit and push your changes.

### Sample Prompt

```text
Review #file:src/dreamguard/claims.py and #file:docs/SERVICE.md. Complete the
service documentation and add useful public API docstrings. Explain only
behavior supported by the code and state that every record is synthetic.
```

### Success Criteria

- `docs/SERVICE.md` explains setup, architecture, rules, and project structure.
- Public types and functions have useful docstrings.
- Comments explain intent rather than restating code.
- A new developer can understand and test DreamGuard using only the docs.

## 2. Custom Instructions

**PIT STOP**

Tailor GitHub Copilot to the team's coding and privacy standards.

### Your Mission

Create `.github/copilot-instructions.md` with the context and conventions Copilot
must follow throughout this repository.

### Enterprise Value

Repository instructions improve consistency across teams, reduce review cycles,
and preserve architecture, quality, and privacy expectations.

### Steps to Complete

1. Stay on the branch created in Challenge 1.
2. Create `.github/copilot-instructions.md`.
3. Describe the Python stack and claims assessment architecture.
4. Require PEP 8 naming, type hints, `Decimal` for money, `unittest`, synthetic
   data only, focused changes, and public API preservation.
5. Test the instructions in a fresh Copilot chat.
6. Commit and push your changes.

### Sample Prompt

```text
Create .github/copilot-instructions.md for DreamGuard. Include project context
and require PEP 8 naming, type hints, Decimal for money, unittest with descriptive
test names, synthetic data only, focused changes, and public API preservation.
```

### Success Criteria

- `.github/copilot-instructions.md` exists with actionable standards.
- Naming, style, architecture, testing, and privacy are covered.
- Copilot-generated code follows the standards in a fresh chat.

## 3. Custom Agent - Spec-Driven Development

**TURBO**

Build a custom Copilot agent that produces approved specifications before code.

### Your Mission

Create a selectable `.agent.md` that runs three sequential phases: **Intent**,
**Design**, and **Tasks + Executive Summary**.

### Enterprise Value

Spec-driven development aligns stakeholders and engineers before implementation,
reducing rework, scope creep, and ambiguity while improving traceability.

### Steps to Complete

1. Create `.github/agents/spec-driven-dev.agent.md`.
2. Phase 1 - Intent: clarify goals, users, constraints, and acceptance criteria.
3. Phase 2 - Design: define architecture, components, data flow, API contracts,
   privacy constraints, and design decisions.
4. Phase 3 - Tasks + Summary: create ordered tasks and an executive summary.
5. Require user approval before proceeding to each next phase.
6. Select the agent from Copilot Chat and test it with the prompt below.
7. In a separate chat, ask the main agent to delegate a specification review to
   the spec-driven development agent as a subagent.
8. Save `intent.md`, `design.md`, `tasks.md`, and `summary.md` under
   `specs/claims-status-notifications/`.
9. Commit and push your changes.

### Create-Agent Prompt

```text
Create .github/agents/spec-driven-dev.agent.md. It must run three sequential
phases and ask for approval after each: Intent, Design, and Tasks + Executive
Summary. Save intent.md, design.md, tasks.md, and summary.md under
specs/[feature-name]/. Each document must build on the approved previous phase.
```

### Test Prompt

```text
I want to add claims-status notifications that use synthetic contact details and
inform a client when a claim becomes pending, referred, approved, or rejected.
```

### Subagent Prompt

```text
Delegate a review of the claims-status notification specifications to the
spec-driven-dev agent as a subagent. Report traceability gaps between intent,
design, and tasks without changing any files.
```

### Success Criteria

- The agent has a clear persona and all three gated phases.
- All four spec documents exist in a feature folder.
- Documents are coherent and traceable across phases.
- The agent can also complete a focused delegated review as a subagent.
- The agent works for feature requests beyond the sample.

## 4. Testing

**FINISH LINE**

Use Copilot to build a test suite that catches claims-rule regressions.

### Your Mission

Cover happy paths, edge cases, and invalid inputs in the DreamGuard assessment
logic.

### Enterprise Value

Automated tests enable confident change, reduce incidents, support continuous
delivery, and protect customer trust.

### Steps to Complete

1. Stay on the branch created in Challenge 1.
2. Generate tests for approval, pending-document, and referral decisions.
3. Add boundary tests and cases for unsupported types and non-positive amounts.
4. Make only the production changes required by the tests.
5. Run the full suite and scorecard.
6. Commit and push your changes.

### Sample Prompts

```text
Write unittest tests for #file:src/dreamguard/claims.py covering approval,
missing documents, waiting-period referral, and the three-month boundary.
```

```text
Add edge-case tests for unsupported claim types and zero or negative amounts,
then make only the production changes required for those tests to pass.
```

### Success Criteria

- At least six well-named tests cover happy paths and edge cases.
- Unsupported types and non-positive amounts cannot be approved.
- All tests pass and `python scripts/score.py` reports 100/100.