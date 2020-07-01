from contextlib import ExitStack as does_not_raise

from django.db import models
import pytest

from strict_fields import apps
from .common import END_OF_2019_AWARE
from .common import END_OF_2019_NAIVE
from .common import LAST_DAY_OF_2019


@pytest.mark.parametrize(
    'settings_parameter, monkey_patch_function',
    (
        (
            'STRICT_FIELDS_HARDEN_DJANGOS_CHARFIELD',
            'monkey_patch_djangos_charfield',
        ),
        (
            'STRICT_FIELDS_HARDEN_DJANGOS_TEXTFIELD',
            'monkey_patch_djangos_textfield',
        ),
        (
            'STRICT_FIELDS_HARDEN_DJANGOS_DATETIMEFIELD',
            'monkey_patch_djangos_datetimefield',
        ),
    ),
)
@pytest.mark.parametrize('enabled', (False, True))
def test_app_ready_monkey_patch_individual(
    mocker, settings, settings_parameter, enabled, monkey_patch_function
):

    mock_monkey_patch_function = mocker.patch(
        f'strict_fields.apps.{monkey_patch_function}', autospec=True,
    )

    setattr(settings, settings_parameter, enabled)

    # Hacky, but valid way to allow us to call an instance method without
    # instantiating the class itself
    mocked_self = object()

    apps.StrictFieldsConfig.ready(mocked_self)

    if enabled:
        mock_monkey_patch_function.assert_called()
    else:
        mock_monkey_patch_function.assert_not_called()


@pytest.mark.parametrize('enabled', (False, True))
def test_app_ready_monkey_patch_all(mocker, settings, enabled):

    mocks = [
        mocker.patch(
            f'strict_fields.apps.monkey_patch_djangos_charfield',
            autospec=True,
        ),
        mocker.patch(
            f'strict_fields.apps.monkey_patch_djangos_textfield',
            autospec=True,
        ),
        mocker.patch(
            f'strict_fields.apps.monkey_patch_djangos_datetimefield',
            autospec=True,
        ),
    ]

    settings.STRICT_FIELDS_HARDEN_DJANGOS_FIELDS = enabled

    # Hacky, but valid way to allow us to call an instance method without
    # instantiating the class itself
    mocked_self = object()

    apps.StrictFieldsConfig.ready(mocked_self)

    for mock in mocks:
        if enabled:
            mock.assert_called()
        else:
            mock.assert_not_called()


@pytest.mark.parametrize(
    'use_tz, value, expected, expected_exception',
    [
        (False, None, None, does_not_raise()),
        (True, None, None, does_not_raise()),
        (False, '2019-12-31T12:34:56-0800', None, pytest.raises(ValueError)),
        (False, LAST_DAY_OF_2019, None, pytest.raises(ValueError)),
        (False, END_OF_2019_AWARE, None, pytest.raises(ValueError)),
        (True, '2019-12-31T12:34:56', None, pytest.raises(ValueError)),
        (True, LAST_DAY_OF_2019, None, pytest.raises(ValueError)),
        (True, END_OF_2019_NAIVE, None, pytest.raises(ValueError)),
    ],
)
def test_monkey_patch_djangos_datetimefield(
    settings, use_tz, value, expected, expected_exception
):
    settings.USE_TZ = use_tz
    apps.monkey_patch_djangos_datetimefield()
    with expected_exception:
        assert models.DateTimeField().get_prep_value(value) == expected
    with expected_exception:
        assert models.DateTimeField().to_python(value) == expected
    apps.disable_monkey_patch_djangos_datetimefield()


def test_monkey_patch_djangos_charfield():
    assert models.CharField()._get_default() == ''
    apps.monkey_patch_djangos_charfield()
    assert models.CharField()._get_default() is None
    apps.disable_monkey_patch_djangos_charfield()
    assert models.CharField()._get_default() == ''


def test_monkey_patch_djangos_textfield():
    assert models.TextField()._get_default() == ''
    apps.monkey_patch_djangos_textfield()
    assert models.TextField()._get_default() is None
    apps.disable_monkey_patch_djangos_textfield()
    assert models.TextField()._get_default() == ''
