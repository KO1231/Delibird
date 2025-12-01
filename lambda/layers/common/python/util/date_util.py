from datetime import datetime, timezone, tzinfo
from zoneinfo import ZoneInfo

JST_TIMEZONE: tzinfo = ZoneInfo("Asia/Tokyo")
UTC_TIMEZONE: tzinfo = timezone.utc


def get_jst_datetime_now():
    return datetime.now(JST_TIMEZONE)


def as_jst(dt: datetime):
    if dt.tzinfo is None:
        raise ValueError("datetime is not timezone-aware.")
    return dt.astimezone(JST_TIMEZONE)


def get_utc_datetime_now():
    return datetime.now(UTC_TIMEZONE)


def as_utc(dt: datetime):
    if dt.tzinfo is None:
        raise ValueError("datetime is not timezone-aware.")
    return dt.astimezone(UTC_TIMEZONE)
