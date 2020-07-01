from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo


class MadeupTz(tzinfo):

    utc_offset = timedelta(hours=1, minutes=23)
    dst_offset = timedelta(minutes=1)

    def utcoffset(self, dt):  # pragma: no cover
        return self.utc_offset + self.dst(dt)

    def fromutc(self, dt):  # pragma: no cover
        # Follow same validations as in datetime.tzinfo
        if not isinstance(dt, datetime):
            raise TypeError("fromutc() requires a datetime argument")
        if dt.tzinfo is not self:
            raise ValueError("dt.tzinfo is not self")

        return dt + self.utc_offset

    def dst(self, dt):  # pragma: no cover
        return self.dst_offset

    def tzname(self, dt):  # pragma: no cover
        return "+01:23"

    def __repr__(self):
        return f"{self.__class__.__name__}()"


END_OF_2019_NAIVE = datetime(2019, 12, 31, 12, 34, 56, 123456)
END_OF_2019_NAIVE_ISOFORMATTED = END_OF_2019_NAIVE.isoformat()
END_OF_2019_AWARE = datetime(
    2019, 12, 31, 12, 34, 56, 123456, tzinfo=MadeupTz()
)
LAST_DAY_OF_2019 = date(2019, 12, 31)
