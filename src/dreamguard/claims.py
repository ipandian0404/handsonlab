"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Immutable claim payload used as input to the risk-assessment workflow.

    Attributes:
        policy_number: Identifier for the synthetic policy record.
        claim_type: Claim category, such as "life" or "disability".
        amount: Requested claim amount represented as a Decimal.
        months_active: Number of months the policy has been active.
        documents: Collection of document identifiers already attached to the record.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClaimDecision:
    """Outcome produced by assessing a single claim.

    Attributes:
        status: Decision status such as "referred", "pending_documents", or "approved".
        approved_amount: Dollar amount approved for payment in the decision.
        reasons: Human-readable explanations for the status.
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def assess_claim(claim: Claim) -> ClaimDecision:
    """Evaluate a single claim against the rules implemented by this service.

    The current implementation only applies two checks:
    - claims with fewer than three active months are marked as "referred";
    - claims outside the waiting period are checked for required documents based on
      claim type before they are marked as "pending_documents" or "approved".

    Unsupported claim types or negative amounts are not validated in this code path.
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


def calculate_payout(approved_amount: Decimal, processing_fee_rate: Decimal = Decimal("0.10")) -> Decimal:
    """Calculate the payout after applying a processing fee.

    Args:
        approved_amount: The approved claim amount as a Decimal (must be >= 0).
        processing_fee_rate: Fee rate to deduct (default 10%).

    Returns:
        A Decimal representing the net payout rounded to cents.

    Raises:
        ValueError: If `approved_amount` is negative or `processing_fee_rate` is out of range.
    """
    if approved_amount < 0:
        raise ValueError("approved_amount must be non-negative")
    if processing_fee_rate < 0 or processing_fee_rate > 1:
        raise ValueError("processing_fee_rate must be between 0 and 1")

    # Calculate fee and net payout using Decimal arithmetic, round to cents
    fee = (approved_amount * processing_fee_rate).quantize(Decimal("0.01"))
    payout = (approved_amount - fee).quantize(Decimal("0.01"))
    return payout
