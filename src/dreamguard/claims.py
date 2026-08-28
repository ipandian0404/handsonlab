"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Represent an immutable synthetic claim submitted for assessment.

    All claims use entirely fictional data. Monetary values use
    :class:`~decimal.Decimal` to avoid floating-point precision issues.

    Attributes:
        policy_number: Fictional policy identifier.
        claim_type: Claim category; only ``life`` and ``disability`` are assessed.
        amount: Requested claim amount as a :class:`~decimal.Decimal`.
        months_active: Duration the policy has been active; must be 3+ to assess.
        documents: Tuple of fictional document identifiers required by the claim type.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Represent the immutable result of assessing a synthetic claim.

    All assessment results are deterministic and based on fictional claim data.

    Attributes:
        status: Outcome of assessment. Valid values are ``rejected``,
            ``referred``, ``pending_documents``, or ``approved``.
        approved_amount: Claim amount approved, or zero if not approved.
        reasons: Tuple of explanatory messages for non-approved outcomes.
            Empty when status is ``approved``.
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a synthetic claim using the current DreamGuard rules.

    Assessment applies the following rules in order:

    1. Unsupported claim types (not ``life`` or ``disability``) are rejected.
    2. Claims with amounts <= zero are rejected.
    3. Claims with ``months_active`` < 3 are referred for waiting period review.
    4. Life claims require ``death_certificate`` and ``identity_document``.
       Disability claims require ``medical_report`` and ``identity_document``.
    5. Missing required documents result in ``pending_documents`` status.
    6. All other claims are approved for the requested amount.

    All input claims are entirely fictional, and decisions are deterministic.

    Args:
        claim: The synthetic claim to assess.

    Returns:
        A decision containing status (``rejected``, ``referred``,
        ``pending_documents``, or ``approved``), approved amount, and reasons.
    """

    # Document requirements are claim-type-specific: identity document is
    # universal; death certificate required for life claims, medical report for disability.
    required_documents = {
        "life": {"death_certificate", "identity_document"},
        "disability": {"medical_report", "identity_document"},
    }

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

    # Waiting period: claims must have been active for 3 months to proceed further.
    if claim.months_active < 3:
        return ClaimDecision("referred", Decimal("0"), ("Waiting period review required",))

    # Find missing documents by set difference; sort for deterministic output.
    missing = required_documents.get(claim.claim_type, set()) - set(claim.documents)
    if missing:
        return ClaimDecision(
            "pending_documents",
            Decimal("0"),
            tuple(f"Missing {document}" for document in sorted(missing)),
        )

    return ClaimDecision("approved", claim.amount, ())