# Importing fields so they can be imported directly from library.
# E.g.:
#     from strict_fields import CharField
import django

from strict_fields.fields import CharField
from strict_fields.fields import DateTimeField
from strict_fields.fields import TextField
from strict_fields.version import __version__

__all__ = ["CharField", "DateTimeField", "TextField", "__version__"]

if django.VERSION < (3, 2):  # pragma: no cover
    default_app_config = "strict_fields.apps.StrictFieldsConfig"

del django
