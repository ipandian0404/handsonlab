"""Core claims assessment logic for the DreamGuard training scenario."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Claim:
    """Represent an immutable synthetic claim submitted for assessment.

    This class holds a complete synthetic claim record with all fields required
    for assessment. All values, including policy numbers, claim types, and
    document identifiers, are fictional and used only for training purposes.

    Attributes:
        policy_number: Fictional identifier for the policy associated with
            the claim. Used as a reference only; not validated.
        claim_type: The type of claim, such as ``"life"`` or ``"disability"``.
            Only certain types are supported; unsupported types trigger rejection.
        amount: The claimed monetary amount as a :class:`~decimal.Decimal`.
            Must be greater than zero; non-positive amounts are rejected.
        months_active: The number of months the associated policy has been active.
            Claims from policies active fewer than three months are referred.
        documents: Immutable tuple of document identifiers (fictional names)
            supplied with the claim, such as ``"death_certificate"`` or
            ``"identity_document"``. Assessed for completeness against
            requirements for the claim type.
    """

    policy_number: str
    claim_type: str
    amount: Decimal
    months_active: int
    documents: tuple[str, ...]


@dataclass(frozen=True)
class ClientContact:
    """Represent synthetic contact details for a claim notification.

    The values are fictional and intended for training examples only. They are
    used solely to demonstrate how a notification might be addressed to a
    client without relying on real personal or financial data.

    Attributes:
        name: Fictional client name.
        email: Fictional email address.
        phone: Fictional phone number.
    """

    name: str
    email: str
    phone: str


@dataclass(frozen=True)
class ClaimDecision:
    """Represent the immutable result of assessing a synthetic claim.

    This class holds the outcome of applying assessment rules to a synthetic
    claim. The decision is deterministic based solely on the claim's contents.

    Attributes:
        status: The assessment outcome as a string. Possible values are:
            ``"approved"`` (claim meets all requirements), ``"rejected"``
            (claim violates policy constraints), ``"referred"`` (claim requires
            manual review due to policy waiting period), or
            ``"pending_documents"`` (required documents are missing).
        approved_amount: The amount approved by the assessment as a
            :class:`~decimal.Decimal`. Zero for non-approved outcomes;
            equal to the requested amount for approved claims.
        reasons: Immutable tuple of explanatory strings describing why a claim
            was not approved. Empty for approved claims. Reasons are sorted
            lexicographically where order matters.
    """

    status: str
    approved_amount: Decimal
    reasons: tuple[str, ...]


def build_notification_message(
    claim: Claim,
    decision: ClaimDecision,
    contact: ClientContact | None = None,
) -> str:
    """Build a human-readable notification for a claim assessment outcome.

    The message is derived from the current decision status and is intended for
    documentation, tests, and simple downstream integrations. The function does
    not change the claim assessment rules or the public decision model.

    Args:
        claim: The synthetic claim that was assessed.
        decision: The assessment decision produced for the claim.
        contact: Optional synthetic contact details to include in the message.

    Returns:
        A deterministic human-readable notification message for the supplied
        decision status.
    """

    status_message = {
        "approved": "Claim approved for the requested amount.",
        "rejected": "Claim rejected because the claim did not satisfy the required rules.",
        "referred": "Claim referred for review because the waiting period has not been completed.",
        "pending_documents": "Claim is pending documents because required documents are missing.",
    }.get(decision.status, "Claim status could not be described.")

    if contact is None:
        return status_message

    if decision.status == "approved":
        summary = "approved"
    elif decision.status == "rejected":
        summary = "rejected"
    elif decision.status == "referred":
        summary = "referred"
    elif decision.status == "pending_documents":
        summary = "pending documents"
    else:
        summary = "updated"

    return (
        f"Hello {contact.name}, your claim {claim.policy_number} is {summary}. "
        f"We will reach you at {contact.email} or {contact.phone}."
    )


def assess_claim(claim: Claim) -> ClaimDecision:
    """Assess a synthetic claim and produce a deterministic decision.

    Applies the DreamGuard assessment rules in sequence to the input claim.
    The decision process is deterministic: identical claims always produce
    identical decisions. No external state or side effects occur; assessment
    does not modify the input claim.

    The rules are applied in this order:

    1. If ``claim_type`` is not ``"life"`` or ``"disability"``, reject with
       reason ``"Unsupported claim type: <type>"``.
    2. If ``amount`` is not positive, reject with reason
       ``"Claim amount must be greater than zero"``.
    3. If ``months_active`` is less than 3, refer with reason
       ``"Waiting period review required"``.
    4. Check that the claim supplies all required documents for its type:
       - ``"life"`` claims require ``"death_certificate"`` and
         ``"identity_document"``.
       - ``"disability"`` claims require ``"medical_report"`` and
         ``"identity_document"``.
    5. If any required documents are missing, return status
       ``"pending_documents"`` with sorted reasons of the form
       ``"Missing <document>"``.
    6. Any claim that passes all rules is approved for its requested amount.

    Args:
        claim: The synthetic claim to assess. Must be a valid Claim instance;
            the function does not validate policy numbers, document names, or
            JSON shape.

    Returns:
        A ClaimDecision with the assessment status, approved amount, and
        explanatory reasons.
    """

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

    if claim.amount is None or claim.amount <= 0:
        return ClaimDecision(
            "rejected",
            Decimal("0"),
            ("Claim amount must be greater than zero",),
        )

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