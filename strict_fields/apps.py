from django.apps import AppConfig
from django.conf import settings
from django.db import models

from . import fields


def monkey_patch_djangos_charfield():
    field = models.CharField
    field._original_empty_strings_allowed = field.empty_strings_allowed
    field.empty_strings_allowed = False


def disable_monkey_patch_djangos_charfield():
    field = models.CharField
    field.empty_strings_allowed = field._original_empty_strings_allowed
    del field._original_empty_strings_allowed


def monkey_patch_djangos_textfield():
    field = models.TextField
    field._original_empty_strings_allowed = field.empty_strings_allowed
    field.empty_strings_allowed = False


def disable_monkey_patch_djangos_textfield():
    field = models.TextField
    field.empty_strings_allowed = field._original_empty_strings_allowed
    del field._original_empty_strings_allowed


def monkey_patch_djangos_datetimefield():
    """
    This is used to enforce stricter rules on usage of the DateTimeField model
    field.

    Use this settings variable to activate this patch:

        STRICT_FIELDS_HARDEN_DJANGOS_DATETIMEFIELD
            Set to `True` to enable this patch. Otherwise, no effective change
            is made to the DateTimeField.

    """
    field = models.DateTimeField

    def djangos_datetimefield_wrapper(fun):
        def wrapped(self, value):
            if value is not None:
                validator = fields.get_datetime_validator()
                validator(value)
            return fun(self, value)

        return wrapped

    field._original_get_prep_value = field.get_prep_value
    field.get_prep_value = djangos_datetimefield_wrapper(field.get_prep_value)
    field._original_to_python = field.to_python
    field.to_python = djangos_datetimefield_wrapper(field.to_python)


def disable_monkey_patch_djangos_datetimefield():
    field = models.DateTimeField
    field.get_prep_value = field._original_get_prep_value
    field.to_python = field._original_to_python
    del field._original_get_prep_value
    del field._original_to_python


class StrictFieldsConfig(AppConfig):
    name = 'strict_fields'

    def ready(self):

        # Execute monkey patching of Django's fields, if enabled

        monkey_patches = set()

        if getattr(settings, 'STRICT_FIELDS_HARDEN_DJANGOS_CHARFIELD', False):
            monkey_patches.add(monkey_patch_djangos_charfield)

        if getattr(settings, 'STRICT_FIELDS_HARDEN_DJANGOS_TEXTFIELD', False):
            monkey_patches.add(monkey_patch_djangos_textfield)

        if getattr(
            settings, 'STRICT_FIELDS_HARDEN_DJANGOS_DATETIMEFIELD', False
        ):
            monkey_patches.add(monkey_patch_djangos_datetimefield)

        if getattr(settings, 'STRICT_FIELDS_HARDEN_DJANGOS_FIELDS', False):
            monkey_patches.add(monkey_patch_djangos_charfield)
            monkey_patches.add(monkey_patch_djangos_textfield)
            monkey_patches.add(monkey_patch_djangos_datetimefield)

        for monkey_patch in monkey_patches:
            monkey_patch()
