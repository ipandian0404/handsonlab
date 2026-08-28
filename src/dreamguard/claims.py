"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Represent an immutable synthetic claim submitted for assessment.

    Monetary values use :class:`~decimal.Decimal`, and ``documents`` contains
    the document identifiers supplied with the claim.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Represent the immutable result of assessing a synthetic claim.

    ``status`` identifies the outcome, ``approved_amount`` is zero unless the
    claim is approved, and ``reasons`` explains non-approved outcomes.
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a synthetic claim using the current DreamGuard rules.

    Unsupported claim types and non-positive amounts are rejected. Valid claims
    active for fewer than three months are referred. Otherwise, life and
    disability claims with missing required documents remain pending. Every
    claim that reaches the final rule is approved for its requested amount.

    Args:
        claim: The synthetic claim to assess.

    Returns:
        A decision containing the status, approved amount, and reasons.
    """

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
