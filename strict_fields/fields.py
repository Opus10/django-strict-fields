from django.conf import settings
from django.db import models

from . import helpers


class CharField(models.CharField):
    """Improves Django's default CharField by not defaulting to the empty
    string.

    Django's default CharField breaks symmetry w.r.t. the other Django basic
    fields (IntegerField, DateField, DecimalField, etc.) in the sense that if
    initialized without specifying a value for the relevant field, Django (or
    the database) will complain about missing values if the field is
    `null=False`. Django's CharField will default to the empty string, which
    likely is not what the developer wants.

    Example:
        class MyTraditionalModel(Model):
            name = models.CharField()

        class MyStrictModel(Model):
            name = strict_fields.CharField()

        # Here we can just create an object, without specifying any particular
        # value for the `name` field.
        >>> MyTraditionalModel.objects.create()
        <MyTraditionalModel: MyTraditionalModel object (1)>

        # Here, in contract, the ORM/database will complain about not setting
        # a value for the `name` field.
        >>> MyStrictModel.objects.create()
        <lots-of-traceback>
        IntegrityError: null value in column "name" violates not-null
        constraint
        DETAIL:  Failing row contains (1, null).
    """

    empty_strings_allowed = False


class TextField(models.TextField):
    """
    Django also defines TextFields without redefining this parameter, see
    CharField docstring for further explanation.
    """

    empty_strings_allowed = False


def get_datetime_validator():
    if settings.USE_TZ is False:
        return helpers.ensure_tz_naive_datetime
    elif settings.USE_TZ is True:
        return helpers.ensure_tz_aware_datetime
    else:
        raise RuntimeError(
            '`settings.USE_TZ` must be either `True` or `False`'
        )


class DateTimeField(models.DateTimeField):
    """Creates either an tz-aware or -unaware datetime field."""

    description = "TZ (un)aware datetime"

    def __init__(self, *args, **kwargs):
        self.validator = get_datetime_validator()
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        if settings.USE_TZ is False:
            return 'timestamp'
        else:
            return 'timestamp with time zone'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        self.validator(value)
        return value

    def get_prep_value(self, value):
        # NOTE: The reason for this is that for example if the programmer has
        # put in place some "before-insert" triggers to set the value auto-
        # matically, we don't want to stop the program from reaching that
        # trigger.
        if value is None:
            return None
        self.validator(value)
        return value
