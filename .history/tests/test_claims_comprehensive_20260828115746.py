"""Comprehensive unit tests for claim assessment logic.

Tests cover approval decisions, missing document handling, waiting period enforcement,
and three-month boundary conditions. All test data is synthetic.
"""

import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dreamguard import Claim, ClaimDecision, assess_claim


class ApprovalDecisionTests(unittest.TestCase):
    """Tests for claims that should receive approved status."""

    def test_assess_claim_approved_when_life_claim_complete_and_waiting_period_met(
        self,
    ):
        """A complete life claim with 3+ months active is approved."""
        claim = Claim(
            policy_number="POL-2001",
            claim_type="life",
            amount=Decimal("250000.00"),
            months_active=24,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(decision.status, "approved", "Life claim should be approved")
        self.assertEqual(
            decision.approved_amount,
            Decimal("250000.00"),
            "Approved amount should match requested amount",
        )
        self.assertEqual(decision.reasons, (), "Approved claim should have no reasons")

    def test_assess_claim_approved_when_disability_claim_complete_and_waiting_period_met(
        self,
    ):
        """A complete disability claim with 3+ months active is approved."""
        claim = Claim(
            policy_number="POL-2002",
            claim_type="disability",
            amount=Decimal("75000.00"),
            months_active=12,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status, "approved", "Disability claim should be approved"
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("75000.00"),
            "Approved amount should match requested amount",
        )
        self.assertEqual(decision.reasons, (), "Approved claim should have no reasons")

    def test_assess_claim_approved_when_life_claim_has_extra_documents(self):
        """A life claim with required documents plus extra documents is approved."""
        claim = Claim(
            policy_number="POL-2003",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=6,
            documents=(
                "death_certificate",
                "identity_document",
                "medical_records",
                "beneficiary_form",
            ),
        )

        decision = assess_claim(claim)

        self.assertEqual(decision.status, "approved", "Life claim with extra docs should be approved")
        self.assertEqual(
            decision.approved_amount,
            Decimal("100000.00"),
            "Approved amount should match requested amount",
        )

    def test_assess_claim_approved_with_large_amount(self):
        """An approved claim can have a large Decimal amount preserved."""
        large_amount = Decimal("1000000.99")
        claim = Claim(
            policy_number="POL-2004",
            claim_type="life",
            amount=large_amount,
            months_active=36,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(decision.status, "approved")
        self.assertEqual(
            decision.approved_amount,
            large_amount,
            "Large amount should be preserved exactly",
        )

    def test_assess_claim_approved_with_small_amount(self):
        """An approved claim can have a small Decimal amount preserved."""
        small_amount = Decimal("0.01")
        claim = Claim(
            policy_number="POL-2005",
            claim_type="disability",
            amount=small_amount,
            months_active=3,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(decision.status, "approved")
        self.assertEqual(
            decision.approved_amount,
            small_amount,
            "Small amount should be preserved exactly",
        )


class MissingDocumentsTests(unittest.TestCase):
    """Tests for claims with missing required documents."""

    def test_assess_claim_pending_when_life_claim_missing_all_documents(self):
        """A life claim with no documents returns pending_documents with sorted reasons."""
        claim = Claim(
            policy_number="POL-3001",
            claim_type="life",
            amount=Decimal("150000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Life claim with no documents should be pending",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("0"),
            "Pending claim should have zero approved amount",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing death_certificate", "Missing identity_document"),
            "Reasons should be sorted and include all missing documents",
        )

    def test_assess_claim_pending_when_life_claim_missing_single_document(self):
        """A life claim missing one required document returns pending_documents."""
        claim = Claim(
            policy_number="POL-3002",
            claim_type="life",
            amount=Decimal("120000.00"),
            months_active=12,
            documents=("death_certificate",),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Life claim with missing document should be pending",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing identity_document",),
            "Reasons should list the missing document",
        )

    def test_assess_claim_pending_when_disability_claim_missing_all_documents(self):
        """A disability claim with no documents returns pending_documents with sorted reasons."""
        claim = Claim(
            policy_number="POL-3003",
            claim_type="disability",
            amount=Decimal("60000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Disability claim with no documents should be pending",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing identity_document", "Missing medical_report"),
            "Reasons should be sorted alphabetically",
        )

    def test_assess_claim_pending_when_disability_claim_missing_medical_report(self):
        """A disability claim missing medical_report returns pending_documents."""
        claim = Claim(
            policy_number="POL-3004",
            claim_type="disability",
            amount=Decimal("50000.00"),
            months_active=12,
            documents=("identity_document",),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Disability claim missing medical_report should be pending",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing medical_report",),
            "Reasons should list the missing medical_report",
        )

    def test_assess_claim_pending_when_disability_claim_missing_identity_document(
        self,
    ):
        """A disability claim missing identity_document returns pending_documents."""
        claim = Claim(
            policy_number="POL-3005",
            claim_type="disability",
            amount=Decimal("45000.00"),
            months_active=12,
            documents=("medical_report",),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Disability claim missing identity_document should be pending",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing identity_document",),
            "Reasons should list the missing identity_document",
        )

    def test_assess_claim_pending_when_life_claim_has_wrong_document_names(self):
        """A life claim with incorrectly spelled document names is treated as missing."""
        claim = Claim(
            policy_number="POL-3006",
            claim_type="life",
            amount=Decimal("80000.00"),
            months_active=12,
            documents=("death_cert", "id_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Life claim with misspelled document names should be pending",
        )
        self.assertEqual(
            len(decision.reasons),
            2,
            "Should identify both correct documents as missing",
        )

    def test_assess_claim_pending_reasons_sorted_alphabetically(self):
        """Missing document reasons are always sorted alphabetically."""
        claim = Claim(
            policy_number="POL-3007",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        # death_certificate comes before identity_document alphabetically
        self.assertEqual(
            decision.reasons,
            ("Missing death_certificate", "Missing identity_document"),
            "Reasons must be sorted alphabetically for deterministic output",
        )


class WaitingPeriodReferralTests(unittest.TestCase):
    """Tests for waiting period enforcement (months_active < 3)."""

    def test_assess_claim_referred_when_life_claim_zero_months_active(self):
        """A life claim with 0 months active is referred due to waiting period."""
        claim = Claim(
            policy_number="POL-4001",
            claim_type="life",
            amount=Decimal("200000.00"),
            months_active=0,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "referred",
            "Claim with 0 months active should be referred",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("0"),
            "Referred claim should have zero approved amount",
        )
        self.assertEqual(
            decision.reasons,
            ("Waiting period review required",),
            "Referred claim should indicate waiting period reason",
        )

    def test_assess_claim_referred_when_life_claim_one_month_active(self):
        """A life claim with 1 month active is referred due to waiting period."""
        claim = Claim(
            policy_number="POL-4002",
            claim_type="life",
            amount=Decimal("150000.00"),
            months_active=1,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "referred",
            "Claim with 1 month active should be referred",
        )
        self.assertEqual(
            decision.reasons,
            ("Waiting period review required",),
        )

    def test_assess_claim_referred_when_disability_claim_two_months_active(self):
        """A disability claim with 2 months active is referred due to waiting period."""
        claim = Claim(
            policy_number="POL-4003",
            claim_type="disability",
            amount=Decimal("55000.00"),
            months_active=2,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "referred",
            "Disability claim with 2 months active should be referred",
        )
        self.assertEqual(
            decision.reasons,
            ("Waiting period review required",),
        )

    def test_assess_claim_referred_takes_precedence_over_missing_documents(self):
        """Waiting period check happens before document check; incomplete claims are still referred."""
        claim = Claim(
            policy_number="POL-4004",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=2,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "referred",
            "Waiting period check should take precedence; claim should be referred, not pending_documents",
        )
        self.assertEqual(
            decision.reasons,
            ("Waiting period review required",),
            "Reason should be waiting period, not missing documents",
        )


class ThreeMonthBoundaryTests(unittest.TestCase):
    """Tests for the three-month waiting period boundary condition."""

    def test_assess_claim_approved_when_life_claim_exactly_three_months_active(self):
        """A life claim with exactly 3 months active meets waiting period and is approved."""
        claim = Claim(
            policy_number="POL-5001",
            claim_type="life",
            amount=Decimal("180000.00"),
            months_active=3,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "approved",
            "Claim at exactly 3 months should pass waiting period check",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("180000.00"),
            "Approved amount should match requested amount",
        )

    def test_assess_claim_approved_when_disability_claim_exactly_three_months_active(
        self,
    ):
        """A disability claim with exactly 3 months active meets waiting period and is approved."""
        claim = Claim(
            policy_number="POL-5002",
            claim_type="disability",
            amount=Decimal("65000.00"),
            months_active=3,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "approved",
            "Disability claim at exactly 3 months should pass waiting period check",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("65000.00"),
        )

    def test_assess_claim_pending_when_life_claim_exactly_three_months_missing_documents(
        self,
    ):
        """A life claim at exactly 3 months with missing documents is pending_documents."""
        claim = Claim(
            policy_number="POL-5003",
            claim_type="life",
            amount=Decimal("110000.00"),
            months_active=3,
            documents=("death_certificate",),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "pending_documents",
            "Claim at 3 months should pass waiting period but fail on documents",
        )
        self.assertEqual(
            decision.reasons,
            ("Missing identity_document",),
            "Should report missing document, not waiting period",
        )

    def test_assess_claim_approved_when_life_claim_four_months_active(self):
        """A life claim with 4 months active (just above boundary) is approved."""
        claim = Claim(
            policy_number="POL-5004",
            claim_type="life",
            amount=Decimal("140000.00"),
            months_active=4,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "approved",
            "Claim with 4 months active should pass waiting period",
        )

    def test_assess_claim_approved_when_life_claim_six_months_active(self):
        """A life claim with 6 months active (well above boundary) is approved."""
        claim = Claim(
            policy_number="POL-5005",
            claim_type="life",
            amount=Decimal("175000.00"),
            months_active=6,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "approved",
            "Claim with 6 months active should pass waiting period",
        )

    def test_assess_claim_boundary_2_months_vs_3_months(self):
        """Confirm boundary: 2 months is referred, 3 months is approved (with full docs)."""
        claim_at_2_months = Claim(
            policy_number="POL-5006",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=2,
            documents=("death_certificate", "identity_document"),
        )
        claim_at_3_months = Claim(
            policy_number="POL-5007",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=3,
            documents=("death_certificate", "identity_document"),
        )

        decision_2_months = assess_claim(claim_at_2_months)
        decision_3_months = assess_claim(claim_at_3_months)

        self.assertEqual(
            decision_2_months.status,
            "referred",
            "Claim at 2 months should be referred",
        )
        self.assertEqual(
            decision_3_months.status,
            "approved",
            "Claim at 3 months should be approved",
        )


class DecisionOutputTypeTests(unittest.TestCase):
    """Tests for correct data types in ClaimDecision output."""

    def test_assess_claim_returns_valid_claim_decision_object(self):
        """assess_claim always returns a ClaimDecision object."""
        claim = Claim(
            policy_number="POL-6001",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertIsInstance(
            decision,
            ClaimDecision,
            "assess_claim should return a ClaimDecision instance",
        )

    def test_assess_claim_approved_amount_is_decimal(self):
        """Approved amount in ClaimDecision is always Decimal type."""
        claim = Claim(
            policy_number="POL-6002",
            claim_type="life",
            amount=Decimal("123456.78"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertIsInstance(
            decision.approved_amount,
            Decimal,
            "Approved amount must be Decimal type",
        )

    def test_assess_claim_reasons_is_tuple_of_strings(self):
        """Reasons in ClaimDecision is always a tuple of strings."""
        claim = Claim(
            policy_number="POL-6003",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertIsInstance(decision.reasons, tuple, "Reasons must be a tuple")
        for reason in decision.reasons:
            self.assertIsInstance(
                reason,
                str,
                f"Each reason must be a string, got {type(reason)}",
            )

    def test_assess_claim_status_is_string(self):
        """Status in ClaimDecision is always a string."""
        claim = Claim(
            policy_number="POL-6004",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertIsInstance(decision.status, str, "Status must be a string")


class UnsupportedClaimTypeTests(unittest.TestCase):
    """Tests for claims with unsupported or invalid claim types."""

    def test_assess_claim_rejected_when_claim_type_unsupported(self):
        """A claim with an unsupported claim type is rejected."""
        claim = Claim(
            policy_number="POL-7001",
            claim_type="travel",
            amount=Decimal("10000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Unsupported claim type should be rejected",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("0"),
            "Rejected claim should have zero approved amount",
        )
        self.assertIn(
            "Unsupported claim type",
            decision.reasons[0],
            "Rejection reason should mention unsupported claim type",
        )

    def test_assess_claim_rejected_when_claim_type_auto_insurance(self):
        """A claim with type 'auto' is rejected as unsupported."""
        claim = Claim(
            policy_number="POL-7002",
            claim_type="auto",
            amount=Decimal("25000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Auto claim should be rejected as unsupported",
        )
        self.assertIn("auto", decision.reasons[0].lower())

    def test_assess_claim_rejected_when_claim_type_home(self):
        """A claim with type 'home' is rejected as unsupported."""
        claim = Claim(
            policy_number="POL-7003",
            claim_type="home",
            amount=Decimal("50000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Home claim should be rejected as unsupported",
        )

    def test_assess_claim_rejected_when_claim_type_empty_string(self):
        """A claim with empty string claim type is rejected."""
        claim = Claim(
            policy_number="POL-7004",
            claim_type="",
            amount=Decimal("10000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Empty claim type should be rejected",
        )

    def test_assess_claim_rejected_for_unsupported_type_takes_precedence_over_waiting_period(
        self,
    ):
        """Unsupported claim type rejection happens regardless of waiting period."""
        claim = Claim(
            policy_number="POL-7005",
            claim_type="unknown",
            amount=Decimal("10000.00"),
            months_active=2,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Unsupported type should be rejected even if in waiting period",
        )
        self.assertIn("Unsupported", decision.reasons[0])


class InvalidAmountTests(unittest.TestCase):
    """Tests for claims with zero or negative amounts."""

    def test_assess_claim_rejected_when_amount_zero(self):
        """A claim with amount zero is rejected."""
        claim = Claim(
            policy_number="POL-8001",
            claim_type="life",
            amount=Decimal("0"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Claim with zero amount should be rejected",
        )
        self.assertEqual(
            decision.approved_amount,
            Decimal("0"),
            "Rejected claim should have zero approved amount",
        )
        self.assertIn(
            "greater than zero",
            decision.reasons[0],
            "Rejection reason should mention positive amount requirement",
        )

    def test_assess_claim_rejected_when_amount_negative(self):
        """A claim with negative amount is rejected."""
        claim = Claim(
            policy_number="POL-8002",
            claim_type="life",
            amount=Decimal("-100.00"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Claim with negative amount should be rejected",
        )
        self.assertIn("greater than zero", decision.reasons[0])

    def test_assess_claim_rejected_when_amount_zero_one_cent(self):
        """A claim with amount $0.01 is approved (minimum valid amount)."""
        claim = Claim(
            policy_number="POL-8003",
            claim_type="disability",
            amount=Decimal("0.01"),
            months_active=3,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "approved",
            "Claim with $0.01 should be approved (valid minimum)",
        )
        self.assertEqual(decision.approved_amount, Decimal("0.01"))

    def test_assess_claim_rejected_for_zero_amount_takes_precedence_over_missing_documents(
        self,
    ):
        """Zero amount rejection happens before document validation."""
        claim = Claim(
            policy_number="POL-8004",
            claim_type="life",
            amount=Decimal("0"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Zero amount should be rejected (not pending_documents)",
        )
        self.assertIn("greater than zero", decision.reasons[0])

    def test_assess_claim_rejected_for_negative_amount_takes_precedence_over_waiting_period(
        self,
    ):
        """Negative amount rejection happens regardless of waiting period."""
        claim = Claim(
            policy_number="POL-8005",
            claim_type="disability",
            amount=Decimal("-50000.00"),
            months_active=2,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Negative amount should be rejected even if in waiting period",
        )
        self.assertIn("greater than zero", decision.reasons[0])

    def test_assess_claim_rejected_for_very_small_negative_amount(self):
        """A claim with very small negative amount (e.g., -$0.01) is rejected."""
        claim = Claim(
            policy_number="POL-8006",
            claim_type="life",
            amount=Decimal("-0.01"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual(
            decision.status,
            "rejected",
            "Negative amount (even tiny) should be rejected",
        )


if __name__ == "__main__":
    unittest.main()
