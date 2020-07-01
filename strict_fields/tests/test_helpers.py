import pytest

from strict_fields import helpers
from .common import END_OF_2019_AWARE
from .common import END_OF_2019_NAIVE
from .common import END_OF_2019_NAIVE_ISOFORMATTED
from .common import LAST_DAY_OF_2019


@pytest.mark.parametrize(
    'value, is_naive', ((END_OF_2019_AWARE, False), (END_OF_2019_NAIVE, True))
)
def test_is_naive(value, is_naive):
    assert helpers.is_naive(value) is is_naive


@pytest.mark.parametrize(
    'is_not_datetime', (None, LAST_DAY_OF_2019, END_OF_2019_NAIVE_ISOFORMATTED)
)
def test_ensure_datetime_not_datetime(is_not_datetime):
    with pytest.raises(ValueError):
        helpers.ensure_datetime(is_not_datetime)


def test_ensure_datetime_is_datetime():
    my_datetime = END_OF_2019_NAIVE
    helpers.ensure_datetime(my_datetime)


@pytest.mark.parametrize(
    'value',
    (
        pytest.param(None, marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(
            LAST_DAY_OF_2019, marks=pytest.mark.xfail(raises=ValueError)
        ),
        pytest.param(
            END_OF_2019_NAIVE_ISOFORMATTED,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            END_OF_2019_AWARE, marks=pytest.mark.xfail(raises=ValueError)
        ),
        END_OF_2019_NAIVE,
    ),
)
def test_ensure_tz_naive_datetime(value):
    helpers.ensure_tz_naive_datetime(value)


@pytest.mark.parametrize(
    'value',
    (
        pytest.param(None, marks=pytest.mark.xfail(raises=ValueError)),
        pytest.param(
            LAST_DAY_OF_2019, marks=pytest.mark.xfail(raises=ValueError)
        ),
        pytest.param(
            END_OF_2019_NAIVE_ISOFORMATTED,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        pytest.param(
            END_OF_2019_NAIVE, marks=pytest.mark.xfail(raises=ValueError)
        ),
        END_OF_2019_AWARE,
    ),
)
def test_ensure_tz_aware_datetime(value):
    helpers.ensure_tz_aware_datetime(value)
