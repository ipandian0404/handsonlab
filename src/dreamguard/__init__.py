"""DreamGuard claims assessment training package.

Provides immutable models and deterministic assessment logic for synthetic
insurance claims. All records are fictional; use only for training and testing.

Public API:
    Claim: Immutable input model for a claim submission.
    ClaimDecision: Immutable output model for an assessment decision.
    assess_claim: Apply DreamGuard decision rules to a single claim.
    load_claims: Load synthetic claims from JSON.
"""

from .claims import Claim, ClaimDecision, assess_claim
from .intake import load_claims

__all__ = ["Claim", "ClaimDecision", "assess_claim", "load_claims"]