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

    def test_valid_claim_file_is_loaded(self):
        claims = load_claims(Path(__file__).parents[1] / "data" / "sample_claims.json")

        self.assertEqual(3, len(claims))
        self.assertEqual("SYN-1001", claims[0].policy_number)


if __name__ == "__main__":
    unittest.main()