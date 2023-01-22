import datetime
import pytz
import pytest
from decimal import Decimal
from prestocard_to_sqlite import service
from . import fixtures
from pathlib import Path


@pytest.mark.parametrize(
    'value, expected_result',
    (
        ('-$3.20', Decimal('-3.20')),
        ('$100.00', Decimal('100.0')),
    )
)
def test_clean_amount(value, expected_result):
    result = service.clean_amount(value)
    assert result == expected_result


def test_process_transaction_history_csv(mocker):
    mocker.patch(
        'prestocard_to_sqlite.service.pd.read_csv',
        return_value=fixtures.PRE_PROCESSED_TRANSACTION_HISTORY,
    )

    df = service.process_transaction_history_csv(Path("TUR_2017_07145993_024.csv"))

    df.equals(fixtures.POST_PROCESSED_TRANSACTION_HISTORY)
