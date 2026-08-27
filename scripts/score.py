"""Score the DreamGuard challenge using lightweight, dependency-free checks."""

from __future__ import annotations

import ast
import io
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))


@dataclass
class Category:
    name: str
    earned: int = 0
    notes: list[str] = field(default_factory=list)

    def add(self, points: int, passed: bool, message: str) -> None:
        if passed:
            self.earned += points
        else:
            self.notes.append(message)


def score_documentation() -> Category:
    result = Category("Documentation")
    service_doc = (ROOT / "docs" / "SERVICE.md").read_text(encoding="utf-8")
    required_sections = (
        "## Purpose",
        "## Architecture",
        "## Claims decision rules",
        "## Data and privacy",
        "## Running the tests",
    )
    complete = "TODO" not in service_doc and all(
        section in service_doc for section in required_sections
    )
    result.add(10, complete, "Complete every section in docs/SERVICE.md.")

    claims_tree = ast.parse((SRC / "dreamguard" / "claims.py").read_text(encoding="utf-8"))
    source_docstrings = {
        node.name: ast.get_docstring(node)
        for node in claims_tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for symbol_name in ("Claim", "ClaimDecision", "assess_claim"):
        documented = bool(source_docstrings.get(symbol_name))
        result.add(5, documented, f"Add a useful docstring to {symbol_name}.")
    return result


def score_tests() -> Category:
    result = Category("Testing")
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    test_count = suite.countTestCases()
    output = io.StringIO()
    run = unittest.TextTestRunner(stream=output, verbosity=0).run(suite)
    result.add(5, run.wasSuccessful(), "Make the complete unit-test suite pass.")
    result.add(5, test_count >= 6, "Add at least six focused tests.")

    test_text = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (ROOT / "tests").glob("test_*.py")
    )
    result.add(5, "pending_documents" in test_text and "referred" in test_text, "Test pending and referral decisions.")
    result.add(5, "unsupported" in test_text, "Test unsupported claim types.")
    result.add(5, "negative" in test_text or "non_positive" in test_text, "Test non-positive amounts.")
    return result


def score_instructions() -> Category:
    result = Category("Custom instructions")
    path = ROOT / ".github" / "copilot-instructions.md"
    exists = path.exists()
    result.add(5, exists, "Create .github/copilot-instructions.md.")
    text = path.read_text(encoding="utf-8").lower() if exists else ""
    checks = (
        ("python" in text and "dreamguard" in text, "Describe the Python DreamGuard context."),
        ("pep 8" in text and "type hint" in text, "Define naming, style, and type-hint standards."),
        ("decimal" in text and "money" in text, "Require Decimal for money."),
        ("unittest" in text and "synthetic" in text and "public api" in text, "Cover tests, privacy, and public APIs."),
    )
    for passed, message in checks:
        result.add(5, passed, message)
    return result


def score_agent() -> Category:
    result = Category("Spec-driven agent")
    path = ROOT / ".github" / "agents" / "spec-driven-dev.agent.md"
    exists = path.exists()
    result.add(5, exists, "Create .github/agents/spec-driven-dev.agent.md.")
    text = path.read_text(encoding="utf-8").lower() if exists else ""
    frontmatter = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    result.add(5, "description:" in frontmatter and "user-invocable: true" in frontmatter, "Make the agent discoverable and user-invocable.")
    phases = ("phase 1", "intent", "phase 2", "design", "phase 3", "tasks", "executive summary")
    result.add(5, all(term in text for term in phases), "Define all three SDD phases.")
    result.add(5, "approve" in text and "next phase" in text, "Require approval before each next phase.")
    specs = ROOT / "specs"
    names = {item.name for item in specs.glob("**/*.md")} if specs.exists() else set()
    result.add(5, {"intent.md", "design.md", "tasks.md", "summary.md"}.issubset(names), "Generate all four spec documents under specs/[feature-name]/.")
    return result


def main() -> int:
    categories = (
        score_documentation(),
        score_instructions(),
        score_agent(),
        score_tests(),
    )
    total = sum(category.earned for category in categories)

    print("\nMomentum Financial Dreams Challenge Score")
    print("=" * 42)
    for category in categories:
        print(f"{category.name:<22} {category.earned:>2}/25")
        for note in category.notes:
            print(f"  - {note}")
    print("-" * 42)
    print(f"TOTAL                  {total:>3}/100")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())