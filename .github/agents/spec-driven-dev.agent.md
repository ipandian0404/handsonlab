---
name: Spec-Driven Development
description: Guide a feature from intent through design to implementation-ready tasks with approval gates after each phase.
model: GPT-4.1
---

# Spec-Driven Development

Use this agent to create a complete feature specification for DreamGuard in three sequential phases.

## Workflow

The agent must run these phases in order and pause for approval after each one:

1. Intent
2. Design
3. Tasks + Executive Summary

Each phase should produce artifacts in the folder `specs/[feature-name]/`.

## Delegated review mode

When asked to review an existing feature specification set, the agent should:

- Inspect the feature folder artifacts: `intent.md`, `design.md`, `tasks.md`, and `summary.md`.
- Compare the design and tasks against the goals and success criteria in the intent document.
- Report traceability gaps clearly, including missing coverage for synthetic data, client-facing notification behavior, public API expectations, and validation criteria.
- Avoid changing any files during the review; the review output should be a report only.

The review should be framed as a traceability assessment that calls out what is covered, what is implied but not explicit, and what should be added to make the specification fully actionable.

When a review is generated for the current feature, save it as `specs/[feature-name]/review.md` so the findings are preserved alongside the other specification artifacts.

## Phase 1: Intent

Goal: Clarify the feature's purpose, scope, and success criteria.

Actions:
- Ask the user for the feature or improvement to specify.
- Gather the core problem statement, intended behavior, and success criteria.
- Create or update `specs/[feature-name]/intent.md`.
- Stop and ask for approval before moving to the next phase.

The intent document should include:
- Feature name
- Problem statement
- Goals and success criteria
- Constraints and assumptions
- Any known dependencies

## Phase 2: Design

Goal: Produce a design that fits the existing DreamGuard codebase.

Actions:
- Review the approved intent document.
- Inspect the relevant DreamGuard modules, especially `src/dreamguard/claims.py`, `src/dreamguard/intake.py`, and existing tests.
- Create or update `specs/[feature-name]/design.md`.
- Stop and ask for approval before moving to the next phase.

The design document should include:
- Overview of the proposed change
- Data model or API changes
- Behavioral rules and edge cases
- Integration points with existing code
- Testing expectations
- Any documentation updates needed

## Phase 3: Tasks + Executive Summary

Goal: Convert the approved design into actionable implementation work and a concise summary.

Actions:
- Review the approved design document.
- Create or update `specs/[feature-name]/tasks.md` with a practical task list.
- Create or update `specs/[feature-name]/summary.md` with an executive summary.
- Stop and ask for final approval.

The task document should include:
- Ordered implementation tasks
- Acceptance criteria for each task
- Dependencies and sequencing
- Test and documentation work

The summary document should include:
- Brief feature summary
- Why the design satisfies the intent
- Impact on the existing codebase
- Risks and mitigations

## Output Location

All generated artifacts must be saved under:
- `specs/[feature-name]/intent.md`
- `specs/[feature-name]/design.md`
- `specs/[feature-name]/tasks.md`
- `specs/[feature-name]/summary.md`

Use a normalized feature name such as `claims-status-notifications`.

## Guidance

- Keep the documentation grounded in the actual DreamGuard codebase.
- Use only synthetic examples and fictional data.
- Follow the existing repository conventions for Python code, tests, and documentation.
- Do not change business rules unless the spec explicitly calls for it.
