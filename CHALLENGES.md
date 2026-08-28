# Momentum Financial Dreams Copilot Enterprise Challenge Race

Race through six enterprise challenges using GitHub Copilot to improve the
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

**FINAL LAP**

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

## 5. Build and Demo

**FINAL LAP**

Build the project and use a browser interface to see the claim-rule changes
working end to end.

### Your Mission

Run the application and verify approved, pending, referred, and rejected
decisions through the DreamGuard Claims Workbench.

### Enterprise Value

A working vertical slice demonstrates that tested domain logic reaches the user
experience and gives reviewers a concrete way to validate behavior.

### Steps to Complete

1. Install the project with `python -m pip install -e .`.
2. Compile with `python -m compileall -q src scripts tests`.
3. Run the complete test suite and scorecard.
4. Start the application with `python app.py`.
5. Open <http://localhost:8000/demo/>.
6. Exercise the Approved, Pending, Referred, and Rejected presets.
7. Edit an amount or document selection and confirm the decision changes.
8. Commit and push the working application.

### Sample Prompt

```text
Build a dependency-free claims assessment UI backed by the existing Python
assess_claim function. Add a small JSON API in app.py, keep all records
synthetic, preserve Decimal values as strings, and verify approved, pending,
referred, and rejected outcomes in the browser.
```

### Success Criteria

- The complete test suite passes and the scorecard reports 100/100.
- The application starts with `python app.py`.
- The workbench calls the Python service instead of duplicating decision rules.
- All four decision states are visible through synthetic scenarios.
- The layout works on desktop and mobile.

## 6. GitLab MCP

**FINISH LINE**

Connect GitHub Copilot in VS Code to GitLab's hosted MCP server. GitLab currently
marks the MCP server as Beta.

### Your Mission

Configure GitLab MCP and verify secure, read-only access to the projects available
to the signed-in user.

### Enterprise Value

MCP gives AI assistants governed access to development context without copying
project data or credentials into prompts.

### Before You Start

- Use a GitLab account that can open at least one project.
- Ask your GitLab administrator to confirm that GitLab Duo, beta and
  experimental features, and MCP server access are enabled.
- You do **not** need to create an access token.

### Click-by-Click Setup

1. In VS Code, press `Ctrl+Shift+P`. The **Command Palette** opens at the top.
2. Type `MCP: Add Server`, then select that exact command.
3. When VS Code asks for the server type, select
   **HTTP (HTTP or Server-Sent Events)**.
4. When VS Code asks for the server URL, paste
   `https://gitlab.com/api/v4/mcp`, then press `Enter`. For GitLab Self-Managed
   or Dedicated, replace only `gitlab.com` with your GitLab instance host.
5. When VS Code asks for a **Server ID**, type `GitLab`, then press `Enter`.
   **You do not obtain this value from GitLab.** It is simply the local display
   name you choose for this connection.
6. When VS Code asks where to save it, select **Workspace** for this lab. Select
   **Global** only if you want the connection in every project.
7. If VS Code asks whether to start the server, select **Start**.
8. Your browser opens GitLab OAuth. Confirm the GitLab address, sign in if
   required, review the access request, and select **Authorize**. Never paste a
   token into VS Code Chat.
9. Return to VS Code, press `Ctrl+Shift+P`, run `MCP: List Servers`, and select
   `GitLab`. Its status should be **Running**.
10. Open a new Copilot Chat, switch to **Agent** mode, select the tools button,
    and confirm that GitLab tools are listed.
11. Paste this read-only verification prompt and review the proposed tool call
    before approving it:

```text
Using GitLab MCP, list my accessible projects. Do not create or modify anything.
```

### If It Does Not Connect

- **No browser opened:** Run `MCP: List Servers`, select `GitLab`, and choose
   **Start** or **Restart**.
- **Access denied or no tools:** Ask your GitLab administrator to verify the
   prerequisites above.
- **Wrong GitLab account:** Sign out of GitLab in the browser, restart the
   server, and repeat OAuth.
- **Wrong URL:** Remove the server and add it again. GitLab.com must use
   `https://gitlab.com/api/v4/mcp`.

Review every requested tool action before approval. MCP tools can encounter
untrusted instructions in issues, merge requests, and repository content, so use
them only with GitLab projects and content you trust. See the
[official GitLab MCP server documentation](https://docs.gitlab.com/user/model_context_protocol/mcp_server/)
for current availability and configuration details.

### Success Criteria

- `GitLab` shows **Running** in `MCP: List Servers`.
- GitLab tools appear in Copilot Chat Agent mode.
- Authentication uses browser OAuth and no token is stored in the repository.
- The read-only verification prompt returns only accessible projects.
- Every MCP tool action is reviewed before approval.