"""Load synthetic claims submitted to the DreamGuard assessment service."""

import json
from decimal import Decimal
from pathlib import Path

from .claims import Claim


def load_claims(path: str | Path) -> list[Claim]:
    with Path(path).open(encoding="utf-8") as claims_file:
        records = json.load(claims_file)

    return [
        Claim(
            policy_number=record["policy_number"],
            claim_type=record["claim_type"],
            amount=Decimal(record["amount"]),
            months_active=record["months_active"],
            documents=tuple(record["documents"]),
        )
        for record in records
    ]