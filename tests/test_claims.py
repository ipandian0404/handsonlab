import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dreamguard import Claim, assess_claim, load_claims


class AssessClaimTests(unittest.TestCase):
    def test_complete_life_claim_is_approved(self):
        claim = Claim(
            policy_number="SYN-1001",
            claim_type="life",
            amount=Decimal("250000.00"),
            months_active=24,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("250000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_life_claim_with_missing_documents_is_pending(self):
        claim = Claim(
            policy_number="SYN-1002",
            claim_type="life",
            amount=Decimal("125000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(
            ("Missing death_certificate", "Missing identity_document"),
            decision.reasons,
        )

    def test_claim_within_waiting_period_is_referred(self):
        claim = Claim(
            policy_number="SYN-1003",
            claim_type="life",
            amount=Decimal("80000.00"),
            months_active=2,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_complete_claim_at_three_month_boundary_is_approved(self):
        claim = Claim(
            policy_number="SYN-1004",
            claim_type="disability",
            amount=Decimal("50000.00"),
            months_active=3,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("50000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_complete_disability_claim_is_approved(self):
        """A disability claim with all required documents is approved."""
        claim = Claim(
            policy_number="SYN-1006",
            claim_type="disability",
            amount=Decimal("5000.00"),
            months_active=12,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("5000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_disability_claim_missing_medical_report(self):
        """A disability claim missing medical_report is pending."""
        claim = Claim(
            policy_number="SYN-1007",
            claim_type="disability",
            amount=Decimal("5000.00"),
            months_active=12,
            documents=("identity_document",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Missing medical_report", decision.reasons)

    def test_disability_claim_missing_identity_document(self):
        """A disability claim missing identity_document is pending."""
        claim = Claim(
            policy_number="SYN-1008",
            claim_type="disability",
            amount=Decimal("5000.00"),
            months_active=12,
            documents=("medical_report",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Missing identity_document", decision.reasons)

    def test_disability_claim_missing_all_documents(self):
        """A disability claim with no documents is pending with all reasons."""
        claim = Claim(
            policy_number="SYN-1009",
            claim_type="disability",
            amount=Decimal("5000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(
            ("Missing identity_document", "Missing medical_report"),
            decision.reasons,
        )

    def test_life_claim_missing_death_certificate_only(self):
        """A life claim missing only death_certificate is pending."""
        claim = Claim(
            policy_number="SYN-1010",
            claim_type="life",
            amount=Decimal("250000.00"),
            months_active=24,
            documents=("identity_document",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Missing death_certificate", decision.reasons)

    def test_waiting_period_at_zero_months_is_referred(self):
        """A claim with 0 months active is referred (waiting period)."""
        claim = Claim(
            policy_number="SYN-1011",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=0,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_waiting_period_at_one_month_is_referred(self):
        """A claim with 1 month active is referred (waiting period)."""
        claim = Claim(
            policy_number="SYN-1012",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=1,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_waiting_period_at_two_months_is_referred(self):
        """A claim with 2 months active is referred (waiting period)."""
        claim = Claim(
            policy_number="SYN-1013",
            claim_type="disability",
            amount=Decimal("50000.00"),
            months_active=2,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_three_month_boundary_exactly_three_months_is_approved(self):
        """A claim with exactly 3 months active passes waiting period."""
        claim = Claim(
            policy_number="SYN-1014",
            claim_type="life",
            amount=Decimal("150000.00"),
            months_active=3,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("150000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_three_month_boundary_just_over_three_months_is_approved(self):
        """A claim with 4 months active passes waiting period."""
        claim = Claim(
            policy_number="SYN-1015",
            claim_type="disability",
            amount=Decimal("75000.00"),
            months_active=4,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("75000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_approval_preserves_requested_amount(self):
        """An approved claim returns the exact requested amount."""
        amounts = [
            Decimal("1.00"),
            Decimal("100.50"),
            Decimal("500000.99"),
        ]

        for amount in amounts:
            with self.subTest(amount=amount):
                claim = Claim(
                    policy_number="SYN-1016",
                    claim_type="life",
                    amount=amount,
                    months_active=12,
                    documents=("death_certificate", "identity_document"),
                )

                decision = assess_claim(claim)

                self.assertEqual("approved", decision.status)
                self.assertEqual(amount, decision.approved_amount)

    def test_waiting_period_takes_precedence_over_missing_documents(self):
        """Waiting period check is applied before document validation."""
        claim = Claim(
            policy_number="SYN-1017",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=2,
            documents=(),
        )

        decision = assess_claim(claim)

        # Should return "referred" (waiting period), not "pending_documents"
        self.assertEqual("referred", decision.status)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_document_reasons_are_sorted_alphabetically(self):
        """Missing document reasons are sorted in the tuple."""
        claim = Claim(
            policy_number="SYN-1018",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        # Expected order: death_certificate comes before identity_document
        self.assertEqual(
            ("Missing death_certificate", "Missing identity_document"),
            decision.reasons,
        )

    def test_unsupported_claim_type_is_rejected(self):
        """A claim with an unsupported type is rejected."""
        claim = Claim(
            policy_number="SYN-1019",
            claim_type="travel",
            amount=Decimal("10000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Unsupported claim type", decision.reasons[0])

    def test_zero_amount_is_rejected(self):
        """A claim with zero amount is rejected."""
        claim = Claim(
            policy_number="SYN-1020",
            claim_type="life",
            amount=Decimal("0"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Claim amount must be greater than zero", decision.reasons[0])

    def test_negative_amount_is_rejected(self):
        """A claim with negative amount is rejected."""
        claim = Claim(
            policy_number="SYN-1021",
            claim_type="disability",
            amount=Decimal("-100.00"),
            months_active=12,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertIn("Claim amount must be greater than zero", decision.reasons[0])

    def test_valid_claim_file_is_loaded(self):
        claims = load_claims(Path(__file__).parents[1] / "data" / "sample_claims.json")

        self.assertEqual(3, len(claims))
        self.assertEqual("SYN-1001", claims[0].policy_number)


if __name__ == "__main__":
    unittest.main()