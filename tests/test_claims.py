import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from dreamguard import Claim, ClientContact, assess_claim, build_notification_message, load_claims


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

    def test_assessment_scenarios_cover_approval_missing_documents_referral_and_boundary(self):
        scenarios = (
            (
                "approval",
                Claim(
                    policy_number="SYN-1004",
                    claim_type="life",
                    amount=Decimal("250000.00"),
                    months_active=24,
                    documents=("death_certificate", "identity_document"),
                ),
                "approved",
                Decimal("250000.00"),
                (),
            ),
            (
                "missing documents",
                Claim(
                    policy_number="SYN-1005",
                    claim_type="life",
                    amount=Decimal("125000.00"),
                    months_active=12,
                    documents=(),
                ),
                "pending_documents",
                Decimal("0"),
                ("Missing death_certificate", "Missing identity_document"),
            ),
            (
                "waiting-period referral",
                Claim(
                    policy_number="SYN-1006",
                    claim_type="life",
                    amount=Decimal("80000.00"),
                    months_active=2,
                    documents=("death_certificate", "identity_document"),
                ),
                "referred",
                Decimal("0"),
                ("Waiting period review required",),
            ),
            (
                "three-month boundary",
                Claim(
                    policy_number="SYN-1007",
                    claim_type="disability",
                    amount=Decimal("50000.00"),
                    months_active=3,
                    documents=("medical_report", "identity_document"),
                ),
                "approved",
                Decimal("50000.00"),
                (),
            ),
        )

        for name, claim, expected_status, expected_amount, expected_reasons in scenarios:
            with self.subTest(case=name):
                decision = assess_claim(claim)

                self.assertEqual(expected_status, decision.status)
                self.assertEqual(expected_amount, decision.approved_amount)
                self.assertEqual(expected_reasons, decision.reasons)

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

    def test_empty_claim_type_is_rejected(self):
        claim = Claim(
            policy_number="SYN-1006",
            claim_type="",
            amount=Decimal("10000.00"),
            months_active=12,
            documents=(),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Unsupported claim type: ",), decision.reasons)

    def test_zero_or_negative_amount_is_rejected(self):
        for amount in (Decimal("0"), Decimal("-1.00"), Decimal("-100.50")):
            with self.subTest(amount=amount):
                claim = Claim(
                    policy_number="SYN-1007",
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

    def test_none_amount_is_rejected(self):
        claim = Claim(
            policy_number="SYN-1008",
            claim_type="life",
            amount=None,
            months_active=12,
            documents=("death_certificate", "identity_document"),
        )

        decision = assess_claim(claim)

        self.assertEqual("rejected", decision.status)
        self.assertEqual(Decimal("0"), decision.approved_amount)
        self.assertEqual(("Claim amount must be greater than zero",), decision.reasons)

    def test_valid_claim_file_is_loaded(self):
        claims = load_claims(Path(__file__).parents[1] / "data" / "sample_claims.json")

        self.assertEqual(3, len(claims))
        self.assertEqual("SYN-1001", claims[0].policy_number)

    def test_notification_message_matches_decision_status(self):
        test_cases = (
            (
                Claim(
                    policy_number="SYN-1007",
                    claim_type="life",
                    amount=Decimal("50000.00"),
                    months_active=24,
                    documents=("death_certificate", "identity_document"),
                ),
                "Claim approved for the requested amount.",
            ),
            (
                Claim(
                    policy_number="SYN-1008",
                    claim_type="travel",
                    amount=Decimal("10000.00"),
                    months_active=12,
                    documents=(),
                ),
                "Claim rejected because the claim did not satisfy the required rules.",
            ),
            (
                Claim(
                    policy_number="SYN-1009",
                    claim_type="life",
                    amount=Decimal("80000.00"),
                    months_active=2,
                    documents=("death_certificate", "identity_document"),
                ),
                "Claim referred for review because the waiting period has not been completed.",
            ),
            (
                Claim(
                    policy_number="SYN-1010",
                    claim_type="disability",
                    amount=Decimal("30000.00"),
                    months_active=6,
                    documents=("identity_document",),
                ),
                "Claim is pending documents because required documents are missing.",
            ),
        )

        for claim, expected_message in test_cases:
            with self.subTest(policy_number=claim.policy_number):
                decision = assess_claim(claim)
                message = build_notification_message(claim, decision)
                self.assertEqual(expected_message, message)

    def test_notification_message_includes_synthetic_contact_details(self):
        claim = Claim(
            policy_number="SYN-1011",
            claim_type="disability",
            amount=Decimal("60000.00"),
            months_active=6,
            documents=("identity_document",),
        )
        decision = assess_claim(claim)
        contact = ClientContact(
            name="Avery Morgan",
            email="avery.morgan@example.invalid",
            phone="+1-555-0100",
        )

        message = build_notification_message(claim, decision, contact)

        self.assertEqual(
            "Hello Avery Morgan, your claim SYN-1011 is pending documents. We will reach you at avery.morgan@example.invalid or +1-555-0100.",
            message,
        )


if __name__ == "__main__":
    unittest.main()