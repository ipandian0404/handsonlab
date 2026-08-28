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
