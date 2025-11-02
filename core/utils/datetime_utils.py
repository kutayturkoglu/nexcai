from datetime import datetime, timedelta

def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def get_relative_day(offset: int):
    date = datetime.now() + timedelta(days=offset)
    return date.strftime("%Y-%m-%d")

def describe_day(offset: int):
    if offset == 0:
        return "today"
    elif offset == 1:
        return "tomorrow"
    elif offset == -1:
        return "yesterday"
    else:
        return f"{abs(offset)} day {'later' if offset > 0 else 'before'}"