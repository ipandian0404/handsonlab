"""Load synthetic claims submitted to the DreamGuard assessment service."""

import json
from decimal import Decimal
from pathlib import Path

from .claims import Claim


def load_claims(path: str | Path) -> list[Claim]:
    """Load synthetic claims from a JSON file and convert to Claim objects.

    Reads a JSON file containing an array of claim records at the top level.
    Each record must have ``policy_number``, ``claim_type``, ``amount``,
    ``months_active``, and ``documents`` fields. The ``amount`` field is
    converted to :class:`~decimal.Decimal`, and ``documents`` is converted
    to an immutable tuple. All values in the file must be fictional; this
    function does not validate that records contain only synthetic data.

    Args:
        path: Path to a JSON file containing an array of claim records.
            Accepts either a string or :class:`~pathlib.Path` object.

    Returns:
        A list of Claim objects, one for each record in the JSON array.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        KeyError: If a record is missing a required field.
        ValueError: If ``amount`` cannot be converted to Decimal.
    """
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