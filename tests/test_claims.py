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

    def test_unsupported_claim_type_is_rejected(self):
        claim = Claim(
            policy_number="SYN-1005",
            claim_type="travel",
            amount=Decimal("10000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: travel",), decision.reasons)

    def test_zero_or_negative_amount_is_rejected(self):
        for amount in (Decimal("0"), Decimal("-1.00")):
            with self.subTest(amount=amount):
                claim = Claim(
                    policy_number="SYN-1006",
                    claim_type="life",
                    amount=amount,
                    months_active=12,
                    documents=("death_certificate", "identity_document"),
                )

                decision = assess_claim(claim)

                self.assertEqual("rejected", decision.status)
                self.assertEqual(Decimal("0"), decision.approved_amount)
                self.assertEqual(
                    ("Claim amount must be greater than zero",),
                    decision.reasons,
                )

    def test_valid_claim_file_is_loaded(self):
        claims = load_claims(Path(__file__).parents[1] / "data" / "sample_claims.json")

        self.assertEqual(3, len(claims))
        self.assertEqual("SYN-1001", claims[0].policy_number)


if __name__ == "__main__":
    unittest.main()