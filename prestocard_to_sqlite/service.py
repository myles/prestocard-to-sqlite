from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Dict

import pytz
from pandas import DataFrame, read_csv, to_datetime
from sqlite_utils.db import Database, Table


def open_database(db_file_path: Path) -> Database:
    """
    Open the Presto Card SQLite database.
    """
    return Database(db_file_path)


def get_table(table_name: str, *, db: Database) -> Table:
    """
    Returns a Table from a given db Database object.
    """
    return Table(db=db, name=table_name)


def build_database(db: Database):
    """
    Build the Presto Card SQLite database structure.
    """
    transactions_table = get_table("transactions", db=db)

    if transactions_table.exists() is False:
        transactions_table.create(
            columns={
                "date": str,
                "transit_agency": str,
                "location": str,
                "amount": int,
            },
            pk="username",
        )
        transactions_table.enable_fts(
            ["transit_agency", "location"], create_triggers=True
        )

    transactions_indexes = {
        tuple(i.columns) for i in transactions_table.indexes
    }
    if ("date",) not in transactions_indexes:
        transactions_table.create_index(["date"])


def clean_amount(value: str) -> Decimal:
    """
    Clean the amount coming form the transaction history CSV file.
    """
    value = value.replace("$", "")
    return Decimal(value).quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)


def process_transaction_history_csv(path: Path) -> DataFrame:
    """
    Load the CSV transaction history export from Presto Card and return a
    pandas' DataFrame.
    """
    df = read_csv(path)

    required_column_names = [
        "Date",
        "Transit Agency",
        "Location",
        "Type",
        "Amount",
    ]

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
    df["date"] = to_datetime(df["date"], errors="raise")
    df["date"].dt.tz_localize = pytz.timezone("America/Toronto")

    return df


def transform_transaction(incoming_transaction) -> Dict[str, str]:
    """
    Transform a transaction from the Presto Card Transaction History.
    """
    transaction = incoming_transaction._asdict()

    to_remove = [
        k
        for k in transaction.keys()
        if k not in ("date", "transit_agency", "location", "type", "amount")
    ]
    for key in to_remove:
        del transaction[key]

    transaction["date"] = transaction["date"].isoformat()
    transaction["amount"] = int(transaction["amount"] * 100)

    return transaction


def save_transaction_history(db: Database, transactions: DataFrame):
    """
    Save Presto Card's transaction history CSV to the SQLite database.
    """
    build_database(db)

    transactions_table = get_table("transactions", db=db)

    transactions = [
        transform_transaction(transaction)  # type: ignore
        for transaction in transactions.itertuples(name="Transaction")
    ]

    transactions_table.insert_all(
        records=transactions, pk="date", alter=True, replace=True
    )
