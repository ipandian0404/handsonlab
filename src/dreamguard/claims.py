"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    required_documents = {
        "life": {"death_certificate", "identity_document"},
        "disability": {"medical_report", "identity_document"},
    }

    if claim.months_active < 3:
        return ClaimDecision("referred", Decimal("0"), ("Waiting period review required",))

    missing = required_documents.get(claim.claim_type, set()) - set(claim.documents)
    if missing:
        return ClaimDecision(
            "pending_documents",
            Decimal("0"),
            tuple(f"Missing {document}" for document in sorted(missing)),
        )

    return ClaimDecision("approved", claim.amount, ())