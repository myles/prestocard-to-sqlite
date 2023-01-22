import datetime
from collections import namedtuple
from decimal import Decimal
from pathlib import Path

import pytest
import pytz

from prestocard_to_sqlite import service

from . import fixtures


@pytest.mark.parametrize(
    "value, expected_result",
    (
        ("-$3.20", Decimal("-3.20")),
        ("$100.00", Decimal("100.0")),
    ),
)
def test_clean_amount(value, expected_result):
    result = service.clean_amount(value)
    assert result == expected_result


def test_process_transaction_history_csv(mocker):
    mocker.patch(
        "prestocard_to_sqlite.service.read_csv",
        return_value=fixtures.PRE_PROCESSED_TRANSACTION_HISTORY,
    )

    df = service.process_transaction_history_csv(
        Path("TUR_2017_07145993_024.csv")
    )

    df.equals(fixtures.POST_PROCESSED_TRANSACTION_HISTORY)


def test_transform_transaction():
    transaction_date = datetime.datetime(
        2022, 1, 9, 16, 38, 47, tzinfo=pytz.timezone("America/Toronto")
    )
    expected_transaction_date = transaction_date.isoformat()

    amount = Decimal("-3.70")
    expected_amount = -370

    TransactionTuple = namedtuple(
        "Transaction", ("date", "transit_agency", "location", "type", "amount")
    )

    transaction = TransactionTuple(
        transaction_date,
        "Toronto Transit Commission",
        "ST ANDREW STATION",
        "Fare Payment",
        amount,
    )

    result = service.transform_transaction(transaction)
    assert result == {
        "date": expected_transaction_date,
        "transit_agency": "Toronto Transit Commission",
        "location": "ST ANDREW STATION",
        "type": "Fare Payment",
        "amount": expected_amount,
    }
