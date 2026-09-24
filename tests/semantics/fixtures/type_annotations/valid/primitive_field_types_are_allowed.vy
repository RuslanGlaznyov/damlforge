
from datetime import date, datetime

struct Point:
    owner: Party
    label: Text
    count: Int
    amount: Decimal
    created: date
    expires: datetime
    active: bool
