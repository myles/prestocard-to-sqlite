import click

from . import service


@click.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    "csv_file",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
def cli(db_path, csv_file):
    """
    Save transaction history from Presto Card to a SQLite database.
    """
    db = service.open_database(db_path)
    transactions = service.process_transaction_history_csv(csv_file)
    service.save_transaction_history(db=db, transactions=transactions)
