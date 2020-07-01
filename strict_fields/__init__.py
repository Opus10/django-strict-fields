# Importing fields so they can be imported directly from library.
# E.g.:
#     from strict_fields import CharField
from .fields import CharField  # noqa
from .fields import DateTimeField  # noqa
from .fields import TextField  # noqa

default_app_config = 'strict_fields.apps.StrictFieldsConfig'
