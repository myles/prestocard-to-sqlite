from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd
import pytz


def clean_amount(value: str) -> Decimal:
    """
    Clean the amount coming form the transaction history CSV file.
    """
    value = value.replace("$", "")
    return Decimal(value).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)


def process_transaction_history_csv(path: Path) -> pd.DataFrame:
    """
    Load the CSV transaction history export from Presto Card and return a
    pandas' DataFrame.
    """
    df = pd.read_csv(path, parse_dates=("Date",))

    required_column_names = ["Date", "Transit Agency", "Location", "Type", "Amount"]

    # We want to ensure that our required column names are represented in the
    # CSV file.
    if set(required_column_names).issubset(df.columns) is False:
        raise ValueError("CSV does not have the required columns we need.")

    df = df[required_column_names]

    df.rename(
        columns={
            "Date": "date",
            "Transit Agency": "transit_agency",
            "Location": "location",
            "Type": "type",
            "Amount": "amount",
        },
        inplace=True,
    )

    # Clean up some columns.
    df["amount"] = df["amount"].apply(clean_amount)
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["date"].dt.tz_localize = pytz.timezone("America/Toronto")

    return df
