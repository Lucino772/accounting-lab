import datetime as dt
from typing import Annotated

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]
datetime_tz = Annotated[dt.datetime, mapped_column(DateTime(timezone=True))]
