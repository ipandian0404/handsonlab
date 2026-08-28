"""Core claims assessment logic for the DreamGuard training scenario.

This module contains the immutable data models and pure assessment function
for claim evaluation. All records are synthetic and contain only fictional
data. This is not a production system and does not communicate with
customers or external systems.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Immutable input model for a submitted insurance claim.

    This model represents a claim submitted for assessment. The claim is
    immutable and will not be modified by `assess_claim()`. All records are
    synthetic and contain only fictional data.

    Attributes:
        policy_number: Unique synthetic policy identifier.
        claim_type: Type of claim: "life" or "disability". Other values
            will result in a "rejected" decision.
        amount: Requested claim amount as Decimal. Must be greater than zero.
            Amounts <= 0 result in a "rejected" decision.
        months_active: Months the policy has been active. Values < 3 result
            in a "referred" decision (waiting period).
        documents: Tuple of provided document identifiers. For "life" claims,
            must include "death_certificate" and "identity_document". For
            "disability" claims, must include "medical_report" and
            "identity_document". Missing documents result in
            "pending_documents" decision.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Immutable output model for a claim assessment decision.

    This model contains the result of applying assessment rules to a submitted
    claim without modifying the original claim.

    Attributes:
        status: One of "approved", "rejected", "referred", or
            "pending_documents":
            - "approved": Claim passed validation and is approved.
            - "rejected": Claim type or amount is invalid.
            - "referred": Claim is in the 3-month waiting period.
            - "pending_documents": Claim is missing required documents.
        approved_amount: The approved claim amount. Always 0 for non-approved
            claims; equals the requested amount for approved claims.
        reasons: Tuple of explanatory reasons. Empty for approved claims;
            populated for rejected, referred, and pending_documents statuses.
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a claim and return a decision without modifying the claim.

    Applies validation rules in order to a claim. This is a pure function:
    it does not modify the input claim and has no side effects. All records
    assessed are synthetic.

    Decision rules applied in order:

    1. **Claim type validation**: If claim type is not "life" or "disability",
       returns status "rejected" with reason "Unsupported claim type: <type>".

    2. **Amount validation**: If amount is not greater than zero, returns
       status "rejected" with reason "Claim amount must be greater than zero".

    3. **Waiting period check**: If months_active < 3, returns status
       "referred" with reason "Waiting period review required" and
       approved_amount of 0.

    4. **Document validation**: For claims outside the waiting period:
       - "life" claims require "death_certificate" and "identity_document"
       - "disability" claims require "medical_report" and "identity_document"
       If any required documents are missing, returns status
       "pending_documents" with approved_amount of 0. Reasons are sorted
       alphabetically and use the form "Missing <document>".

    5. **Approval**: Claims passing all checks return status "approved" with
       the requested amount and no reasons (empty tuple).

    Args:
        claim: A Claim object to assess. Will not be modified.

    Returns:
        A ClaimDecision object with status, approved_amount, and reasons.
    """
    required_documents = {
        "life": {"death_certificate", "identity_document"},
        "disability": {"medical_report", "identity_document"},
    }

    # Validate claim type
    if claim.claim_type not in required_documents:
        return ClaimDecision(
            "rejected",
            Decimal("0"),
            (f"Unsupported claim type: {claim.claim_type}",),
        )

    # Validate amount
    if claim.amount <= Decimal("0"):
        return ClaimDecision(
            "rejected",
            Decimal("0"),
            ("Claim amount must be greater than zero",),
        )

    # Check waiting period
    if claim.months_active < 3:
        return ClaimDecision("referred", Decimal("0"), ("Waiting period review required",))

    # Check required documents
    missing = required_documents[claim.claim_type] - set(claim.documents)
    if missing:
        return ClaimDecision(
            "pending_documents",
            Decimal("0"),
            tuple(f"Missing {document}" for document in sorted(missing)),
        )

    return ClaimDecision("approved", claim.amount, ())
