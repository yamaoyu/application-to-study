from datetime import date


def format_date(parsed_date: date) -> str:
    return f"{parsed_date.year}-{parsed_date.month}-{parsed_date.day}"


def parse_activity_date(date_str: str) -> date:
    year, month, day = map(int, date_str.split("-"))
    return date(year=year, month=month, day=day)
