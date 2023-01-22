import datetime
from decimal import Decimal

import pandas as pd
import pytz

PRE_PROCESSED_TRANSACTION_HISTORY = pd.DataFrame(
    columns=["Date", "Transit Agency", "Location", "Type", "Amount"],
    data=(
        (
            "1/9/2022 4:38:47 PM",
            "Toronto Transit Commission",
            "ST ANDREW STATION",
            "Fare Payment",
            "-$3.70",
        ),
    ),
)

POST_PROCESSED_TRANSACTION_HISTORY = pd.DataFrame(
    columns=["date", "transit_agency", "location", "type", "amount"],
    data=(
        (
            datetime.datetime(
                2022, 1, 9, 16, 38, 47, tzinfo=pytz.timezone("America/Toronto")
            ),
            "Toronto Transit Commission",
            "ST ANDREW STATION",
            "Fare Payment",
            Decimal("-3.70"),
        ),
    ),
)
