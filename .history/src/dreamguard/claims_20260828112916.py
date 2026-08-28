"""Core claims assessment logic for the DreamGuard training scenario.

This module provides immutable models and deterministic decision logic for claim
assessment. All data in this service is synthetic and for training purposes only.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Immutable representation of a submitted insurance claim.

    Attributes:
        policy_number: Unique identifier for the policy associated with this claim.
        claim_type: Type of claim (e.g., "life" or "disability").
        amount: The requested claim amount as a Decimal for precision.
        months_active: Duration the policy has been active in months.
        documents: Tuple of document identifiers submitted with the claim.

    Notes:
        - All records in this repository are synthetic.
        - The `amount` field should be positive; validation is deferred to `assess_claim`.
        - The `documents` tuple is immutable; document names are identifiers provided
          by the submitter.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Immutable representation of a claim assessment decision.

    Attributes:
        status: The decision status. Possible values:
            - "approved": Claim is approved for the requested amount.
            - "referred": Claim requires manual review (e.g., waiting period not met).
            - "pending_documents": Claim is incomplete; additional documents required.
        approved_amount: The approved amount as a Decimal. Zero if not approved.
        reasons: Tuple of explanatory strings describing the decision. Empty if approved.

    Notes:
        - All records in this repository are synthetic.
        - The `reasons` tuple is immutable and typically populated when status is not "approved".
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a submitted claim and return a deterministic decision.

    This function evaluates a claim against the following rules in order:

    1. **Waiting period check**: If `months_active` < 3, return status "referred"
       with approved amount 0 and reason "Waiting period review required".
    2. **Required documents check**: For claims beyond the waiting period:
       - Life claims require: death_certificate, identity_document
       - Disability claims require: medical_report, identity_document
       If any required documents are missing, return status "pending_documents" with
       approved amount 0 and sorted reasons like "Missing <document>".
    3. **Approval**: If all checks pass, return status "approved" with the requested
       amount and no reasons.

    Args:
        claim: A `Claim` object to assess.

    Returns:
        A `ClaimDecision` containing the status, approved amount, and reasons.

    Notes:
        - All records in this repository are synthetic.
        - The function does not modify the input claim.
        - Claim type and amount validation are not currently performed.
        - Document validation is case-sensitive exact matching.

    Example:
        >>> from decimal import Decimal
        >>> claim = Claim(
        ...     policy_number="POL-001",
        ...     claim_type="life",
        ...     amount=Decimal("100000"),
        ...     months_active=12,
        ...     documents=("death_certificate", "identity_document")
        ... )
        >>> decision = assess_claim(claim)
        >>> print(decision.status)
        approved
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
