import datetime


def is_naive(datetime_or_time):
    """
    An object of type time or datetime may be naive or aware.
    A datetime object d is aware if
        d.tzinfo is not None and d.tzinfo.utcoffset(d) does not return None.
    d is naive.
        If d.tzinfo is None
        or if d.tzinfo is not None but d.tzinfo.utcoffset(d) returns None,

    A time object t is aware if t.tzinfo is not None and
    t.tzinfo.utcoffset(None) does not return None. Otherwise, t is naive.
    """
    return datetime_or_time.tzinfo is None


def ensure_datetime(value):
    if not isinstance(value, datetime.datetime):
        raise ValueError(f'{value!r} should be a datetime')


def ensure_tz_naive_datetime(value):
    ensure_datetime(value)
    if not is_naive(value):
        raise ValueError(f'This should NOT be tz-aware: {value!r}')


def ensure_tz_aware_datetime(value):
    ensure_datetime(value)
    if is_naive(value):
        raise ValueError(f'This should be tz-aware: {value!r}')
