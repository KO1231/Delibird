from datetime import datetime, timezone, timedelta

from pynamodb.attributes import Attribute
from pynamodb.constants import STRING

_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


class DateTimeAttribute(Attribute[datetime]):
    attr_type = STRING

    def serialize(self, value: datetime):
        if not isinstance(value, datetime):
            raise ValueError("Value '{}' is not a datetime object".format(value))
        if value.tzinfo is None:
            raise ValueError("Naive datetime objects are not supported. Datetime must be timezone aware.")

        fmt = value.strftime(_DATETIME_FORMAT).zfill(31)
        return fmt

    def deserialize(self, value):
        return self._fast_parse_date_string(value)

    @staticmethod
    def _is_timezone(s: str):
        _int = int
        # tzは-12:00から+14:00までの範囲
        return s.isdecimal() and s.isascii() and len(s) == 4 and (0 <= _int(s[0:2]) <= 14) and (0 <= _int(s[2:4]) <= 59)

    @staticmethod
    def _fast_parse_date_string(date_string: str) -> datetime:
        # Method to quickly parse strings formatted with '%Y-%m-%dT%H:%M:%S.%f+0000'.
        # This is ~5.8x faster than using strptime and 38x faster than dateutil.parser.parse.
        _int = int  # Hack to prevent global lookups of int, speeds up the function ~10%
        try:
            # Fix pre-1000 dates serialized on systems where strftime doesn't pad w/older PynamoDB versions.
            date_string = date_string.zfill(31)
            if (len(date_string) != 31 or date_string[4] != '-' or date_string[7] != '-'
                    or date_string[10] != 'T' or date_string[13] != ':' or date_string[16] != ':'
                    or date_string[19] != '.' or (date_string[26] != "+" and date_string[26] != "-")
                    or (not DateTimeAttribute._is_timezone(date_string[27:31]))):
                raise ValueError("Datetime string '{}' does not match format '{}'".format(date_string, _DATETIME_FORMAT))
            return datetime(
                _int(date_string[0:4]), _int(date_string[5:7]), _int(date_string[8:10]),
                _int(date_string[11:13]), _int(date_string[14:16]), _int(date_string[17:19]),
                _int(date_string[20:26]), timezone(timedelta(
                    seconds=(_int(date_string[27:29]) * 3600 + _int(date_string[29:31]) * 60) * (1 if date_string[26] == "+" else -1)))
            )
        except (TypeError, ValueError):
            raise ValueError("Datetime string '{}' does not match format '{}'".format(date_string, _DATETIME_FORMAT))


if __name__ == "__main__":
    from zoneinfo import ZoneInfo
    from datetime import tzinfo

    JST_TIMEZONE: tzinfo = ZoneInfo("Asia/Tokyo")
    UTC_TIMEZONE: tzinfo = timezone.utc
    LOS_TIMEZONE: tzinfo = ZoneInfo("America/Los_Angeles")


    def get_now(tz):
        return datetime.now(tz)


    print(DateTimeAttribute.serialize(None, value=get_now(JST_TIMEZONE))[29:31])
    # +09:00
    print(DateTimeAttribute._fast_parse_date_string(DateTimeAttribute.serialize(None, value=get_now(JST_TIMEZONE))))
    # +00:00
    print(DateTimeAttribute._fast_parse_date_string(DateTimeAttribute.serialize(None, value=get_now(UTC_TIMEZONE))))
    # -08:00 or -07:00
    print(DateTimeAttribute._fast_parse_date_string(DateTimeAttribute.serialize(None, value=get_now(LOS_TIMEZONE))))
