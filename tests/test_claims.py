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

    def test_complete_disability_claim_is_approved(self):
        claim = Claim(
            policy_number="SYN-1007",
            claim_type="disability",
            amount=Decimal("35000.00"),
            months_active=36,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("35000.00"), decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_life_claim_with_only_missing_identity_document_is_pending(self):
        claim = Claim(
            policy_number="SYN-1008",
            claim_type="life",
            amount=Decimal("150000.00"),
            months_active=12,
            documents=("death_certificate",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Missing identity_document",), decision.reasons)

    def test_life_claim_with_only_missing_death_certificate_is_pending(self):
        claim = Claim(
            policy_number="SYN-1009",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=12,
            documents=("identity_document",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Missing death_certificate",), decision.reasons)

    def test_disability_claim_with_missing_documents_is_pending(self):
        claim = Claim(
            policy_number="SYN-1010",
            claim_type="disability",
            amount=Decimal("45000.00"),
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

    def test_disability_claim_with_only_missing_medical_report_is_pending(self):
        claim = Claim(
            policy_number="SYN-1011",
            claim_type="disability",
            amount=Decimal("30000.00"),
            months_active=12,
            documents=("identity_document",),
        )

        decision = assess_claim(claim)

        self.assertEqual("pending_documents", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Missing medical_report",), decision.reasons)

    def test_claim_just_below_three_month_boundary_is_referred(self):
        claim = Claim(
            policy_number="SYN-1012",
            claim_type="life",
            amount=Decimal("200000.00"),
            months_active=2,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_claim_at_one_month_is_referred(self):
        claim = Claim(
            policy_number="SYN-1013",
            claim_type="disability",
            amount=Decimal("50000.00"),
            months_active=1,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_claim_at_zero_months_is_referred(self):
        claim = Claim(
            policy_number="SYN-1014",
            claim_type="life",
            amount=Decimal("100000.00"),
            months_active=0,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("referred", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Waiting period review required",), decision.reasons)

    def test_large_approved_amount_is_preserved(self):
        large_amount = Decimal("1000000.00")
        claim = Claim(
            policy_number="SYN-1015",
            claim_type="life",
            amount=large_amount,
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(large_amount, decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_small_approved_amount_is_preserved(self):
        small_amount = Decimal("0.01")
        claim = Claim(
            policy_number="SYN-1016",
            claim_type="disability",
            amount=small_amount,
            months_active=12,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(small_amount, decision.approved_amount)
        self.assertEqual((), decision.reasons)

    def test_very_small_positive_amount_is_approved(self):
        claim = Claim(
            policy_number="SYN-1017",
            claim_type="life",
            amount=Decimal("0.001"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("approved", decision.status)
        self.assertEqual(Decimal("0.001"), decision.approved_amount)

    def test_uppercase_claim_type_is_unsupported(self):
        claim = Claim(
            policy_number="SYN-1018",
            claim_type="LIFE",
            amount=Decimal("50000.00"),
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: LIFE",), decision.reasons)

    def test_mixed_case_claim_type_is_unsupported(self):
        claim = Claim(
            policy_number="SYN-1019",
            claim_type="Disability",
            amount=Decimal("30000.00"),
            months_active=12,
            documents=("medical_report", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: Disability",), decision.reasons)

    def test_empty_claim_type_is_unsupported(self):
        claim = Claim(
            policy_number="SYN-1020",
            claim_type="",
            amount=Decimal("25000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: ",), decision.reasons)

    def test_claim_type_with_whitespace_is_unsupported(self):
        claim = Claim(
            policy_number="SYN-1021",
            claim_type="life ",
            amount=Decimal("40000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: life ",), decision.reasons)

    def test_very_large_negative_amount_is_rejected(self):
        claim = Claim(
            policy_number="SYN-1022",
            claim_type="life",
            amount=Decimal("-999999999.99"),
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

    def test_amount_just_below_zero_is_rejected(self):
        claim = Claim(
            policy_number="SYN-1023",
            claim_type="disability",
            amount=Decimal("-0.0001"),
            months_active=12,
            documents=("medical_report", "identity_document"),
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