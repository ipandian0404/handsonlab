"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Immutable insurance claim input model.
    
    Represents a synthetic insurance claim with policy and document information
    for assessment. All data in this training service is synthetic.
    
    Attributes:
        policy_number: Unique policy identifier (synthetic).
        claim_type: Type of claim—'life' or 'disability' (synthetic).
        amount: Requested payout amount as Decimal (synthetic monetary value).
        months_active: Duration policy has been active.
        documents: Tuple of document identifiers provided with the claim.
    """
    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Immutable claim assessment output model.
    
    Represents the deterministic decision outcome from assessing a claim.
    Status and amounts are based on the decision rules; reasons explain
    the decision.
    
    Attributes:
        status: Decision outcome—'approved', 'rejected', 'referred', or
            'pending_documents'.
        approved_amount: Decimal amount approved (0 if not approved).
        reasons: Tuple of explanatory messages (empty if approved).
    """
    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Apply deterministic decision rules to a claim.
    
    Assesses a claim without modifying it and returns a decision. Decision rules
    are applied in this order:
    
    1. If months_active < 3, returns status 'referred' (waiting period).
    2. If the claim type is not 'life' or 'disability', returns status 'rejected'.
    3. If the amount is <= 0, returns status 'rejected'.
    4. For 'life' claims, requires 'death_certificate' and 'identity_document'.
       For 'disability' claims, requires 'medical_report' and 'identity_document'.
    5. If any required documents are missing, returns status 'pending_documents'
       with reasons listing each missing document (sorted).
    6. Otherwise returns status 'approved' with the requested amount.
    
    Args:
        claim: Immutable Claim object to assess.
    
    Returns:
        ClaimDecision with status, approved_amount, and reasons tuple.
    """
    required_documents = {
        "life": {"death_certificate", "identity_document"},
        "disability": {"medical_report", "identity_document"},
    }

    if claim.months_active < 3:
        return ClaimDecision("referred", Decimal("0"), ("Waiting period review required",))

    if claim.claim_type not in required_documents:
        return ClaimDecision(
            "rejected",
            Decimal("0"),
            (f"Unsupported claim type: {claim.claim_type}",),
        )

    if claim.amount <= 0:
        return ClaimDecision(
            "rejected",
            Decimal("0"),
            ("Claim amount must be greater than zero",),
        )

    missing = required_documents[claim.claim_type] - set(claim.documents)
    if missing:
        return ClaimDecision(
            "pending_documents",
            Decimal("0"),
            tuple(f"Missing {document}" for document in sorted(missing)),
        )

    return ClaimDecision("approved", claim.amount, ())
