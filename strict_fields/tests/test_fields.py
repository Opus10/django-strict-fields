from django.db import models
import pytest

import strict_fields
from .common import END_OF_2019_AWARE
from .common import END_OF_2019_NAIVE


@pytest.mark.parametrize('model_name', [('CharField'), ('TextField')])
def test_original_fields_get_default(model_name):
    # NOTE: Including this here to showcase the problem with the default
    # behavior of Django's CharField - useful as a reference to the test(s)
    # below.
    field = getattr(models, model_name)()
    assert field.get_default() == ''


@pytest.mark.parametrize('model_name', [('CharField'), ('TextField')])
def test_strict_fields_get_default(model_name):
    field = getattr(strict_fields, model_name)()
    assert field.get_default() is None


def test_datetimefield_invalid_use_tz(settings):
    settings.USE_TZ = 'Neither `True` nor `False`'
    with pytest.raises(RuntimeError):
        strict_fields.DateTimeField()


@pytest.mark.parametrize(
    'use_tz, expected_type',
    ((False, 'timestamp'), (True, 'timestamp with time zone')),
)
def test_datetimefield_db_type(mocker, settings, use_tz, expected_type):
    settings.USE_TZ = use_tz
    field = strict_fields.DateTimeField()
    connection = mocker.Mock()
    assert field.db_type(connection) == expected_type


@pytest.mark.parametrize(
    'use_tz, value',
    [
        # use_tz cases:
        pytest.param(
            False,
            END_OF_2019_AWARE,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        (False, END_OF_2019_NAIVE),
        # TZ-aware cases:
        pytest.param(
            True, END_OF_2019_NAIVE, marks=pytest.mark.xfail(raises=ValueError)
        ),
        (True, END_OF_2019_AWARE),
        # blank value
        (False, None),
        (True, None),
    ],
)
def test_datetimefield_from_db_value(mocker, settings, use_tz, value):
    settings.USE_TZ = use_tz
    field = strict_fields.DateTimeField()
    expression = mocker.Mock()
    connection = mocker.Mock()
    from_db = field.from_db_value(value, expression, connection)
    assert from_db == value


@pytest.mark.parametrize(
    'use_tz, value',
    [
        # use_tz cases:
        pytest.param(
            False,
            END_OF_2019_AWARE,
            marks=pytest.mark.xfail(raises=ValueError),
        ),
        (False, None),
        (False, END_OF_2019_NAIVE),
        # TZ-aware cases:
        pytest.param(
            True, END_OF_2019_NAIVE, marks=pytest.mark.xfail(raises=ValueError)
        ),
        (True, None),
        (True, END_OF_2019_AWARE),
    ],
)
def test_datetimefield_get_prep_value(settings, use_tz, value):
    settings.USE_TZ = use_tz
    field = strict_fields.DateTimeField()
    prep_value = field.get_prep_value(value)
    assert prep_value == value
