from datetime import date, datetime


def to_date(value: str, fmt: str = "%Y-%m-%d") -> date:
    return datetime.strptime(value, fmt).date()
