# django-strict-fields

This library is meant to help enforce stricter rules around using some of the basic model fields that Django provides.

It's done in two ways:

1.  Subclassing Django's fields, and modify them to behave in a more constrained way, or
2.  Introducing settings that, if enabled, will monkey patch Django's fields.

It is advised to opt for option #1 if the idea is to start to gently introduce this into the codebase, but option #2 could be put to use immediately in a unit test suite, allowing to capture immediate problems indcuded via the unit tests.

The problematic fields from Django tackled by this library are:

* CharField
* TextField
* DateTimeField

## CharField & TextField

When a `CharField(null=False)` is instantiated without specifying a value, Django for some reason inserts the empty string into the field. This is in stark contrast to most other fields--for example if one tries to save a new instance of a model containing `IntegerField(null=False)` without specifying the value, Django will raise an `IntegrityError`. `TextField` suffers from the same problem.

This means that if a developer creates a "not-null" `IntegerField` and forgets to explicitly give it a value when instantiating a model object, she will get an exception. However, if doing the same exact thing with a "not-null" `CharField`, Django won't complain, but will insert the empty string into the database.

The same goes for `TextField` as with `CharField`.

The exact reasoning for this decision is unclear, as the changesets introducing this are no longer available via Django's source control system. Seems to have been lost when transitioning from a private Subversion repository to the public git one. Most likely, the feature is there to support older databases where empty-string may be equated with `NULL` values. In most modern SQL databases, this does not seem to be typical.

The strict versions of these fields amend this, and make it so that Django will raise an exception if used without either giving the field a default, or giving a model instance a value for that field prior to saving.

To illustrate the behavior of the strict `CharField` as compared to Django's, here is an example:

    # From models.py:

    class MyBasicModel(models.Model):
        name = models.CharField(max_length=10)

    class MyStrictModel(models.Model):
        name = strict_fields.CharField(max_length=10)

    # Usage in shell:

    >>> lax_instance = MyBasicModel.objects.create()
    <MyBasicModel: MyBasicModel object (1)>
    >>> assert lax_instance.name == ''  # Defaulted to the empty string!
    >>> MyStrictModel.objects.create()
    ...
    IntegrityError: null value in column "name" violates not-null constraint
    DETAIL:  Failing row contains (1, null).

With the strict `CharField`/`TextField`, it's harder to accidentally forget to set the `name` value when using the model. The developer is forced to explicitly set this field like many other core Django fields (`IntegerField`, `DateTimeField`, etc).


There are new settings parameter to monkey patch either field to be strict:

* `STRICT_FIELDS_HARDEN_DJANGOS_CHARFIELD = True`
* `STRICT_FIELDS_HARDEN_DJANGOS_TEXTFIELD = True`

These parameters are inspected when Django is launched and relevant fields are monkey-patched to behave as desired.

*NOTE*: This requires that `'strict_fields'` be put in `settings.INSTALLED_APPS`, so that the monkey-patch functions are called on startup of Django.

*NOTE*: Monkey-patching is generally not considered good practice, as it may have unintended consequences. A read-through of :file:`strict_fields/apps.py` is highly recommended.

## DateTimeField

Django has some support for timezones when using the `DateTimeField`, but it is a fairly crude approach, as if you set `USE_TZ = True`, all `DateTimeField` s will become timezone aware, when it's possible that the developer will have some datetime fields that should be timezone aware, and some that shouldn't. This could lead a developer to store local datetime values as being in UTC, which could lead to much confusion down the road.

A much bigger problem is that Django is very lax with how it handles dates and datetimes. The developer can instantiate and save a model instance with a timezone aware `DateTimeField` and supply a string, a `date`, a naive `datetime` or an timezone aware `datetime`. It _does_ produce warnings to `stdout` (using python's `warning` module), but these often go unnoticed, and these won't break tests.

*Side-note on not supporting strings*: If we want to allow strings as input into the `DateTimeField`, we have a new problem: Parsing! While it seems trivial, it's far from trivial. Should it support ISO 8601? What about ambiguous cases for IS 8601? Do we support more human-friendly formats, like `10/12/19`? Is this MM/DD/YY or DD/MM/YY? It seems far safer to keep parsing out of it, and only support `datetime` objects.

Thus, this library provides you with a hardened version of these, making it much harder to accidentally let things slide until a problem is discovered, and much effort may be needed to rectify a lot of bad data in production.

This is best shown by example. Let's imagine we have these models:

    # Assuming USE_TZ = True in Django settings

    class MyBasicModel(models.Model):
        my_datetime = models.DateTimeField()

    class MyStrictModel(models.Model):
        my_datetime = strict_fields.DateTimeField()

Now, assuming that:

* `print_iso_in_pacific_time()` is an available function with the obvious functionality,
* `my_date` is a `date` object representing `2019-12-31`,
* `my_naive_datetime` is a `datetime` object representing `2019-12-31T23:59:14.123456` and
* `my_aware_datetime` is a `datetime` object representing `2019-12-31T23:59:14.123456-08:00`,

Here are a few examples of how Django's `DateTimeField` will behave when used (note that the `obj` would have to be refreshed from the database, but we're skipping it here for brevity and clarity):

    >>> # Using a TZ-aware ISO-formatted string. This seems a good and legit case.
    >>> obj = MyBasicModel.objects.create(my_datetime='2019-12-31 23:59:14.123456-08:00')
    >>> print_iso_in_pacific_time(obj.my_datetime)
    2019-12-31 23:59:14.123456-08:00

    >>> # Using a naive ISO-formatted string. This very likely leads to problems.
    >>> obj = MyBasicModel.objects.create(my_datetime='2019-12-31 23:59:14.123456')
    >>> # Notice how the hour-value changed from 23 to 15, because the input
    >>> # string was interpreted/assumed to be UTC (this may depend on the
    >>> # local time of the server and/or database).
    >>> print_iso_in_pacific_time(obj.my_datetime)
    2019-12-31 15:59:14.123456-08:00

    >>> # Using only an ISO-formatted date. This very likely leads to problems.
    >>> obj = MyBasicModel.objects.create(my_datetime='2019-12-31')
    >>> # Django assumed the user meant midnight, UTC, so the results may be
    >>> # surprising to the end-user:
    >>> print_iso_in_pacific_time(obj.my_datetime)
    2019-12-30 16:00:00-08:00

    >>> # Using a `date` object. This very likely leads to problems.
    >>> obj = MyBasicModel.objects.create(my_datetime=my_date)
    >>> # Django again assumed the user meant midnight, UTC, yielding some
    >>> # surprising results:
    >>> print_iso_in_pacific_time(obj.my_datetime)
    2019-12-30 16:00:00-08:00

And here are the same use-cases when using the strict `DateTimeField`:

    >>> # Using strings is disallowed:
    >>> obj = MyStrictModel.objects.create(my_datetime='2019-12-31 23:59:14.123456')
    ValueError('Must be TZ-aware datetime')

    >>> # Passing in `date` or naive `datetime` is also barred:
    >>> obj = MyStrictModel.objects.create(my_datetime=my_date)
    ValueError('Must be TZ-aware datetime')
    >>> obj = MyStrictModel.objects.create(my_datetime=my_naive_datetime)
    ValueError('Must be TZ-aware datetime')

    >>> # Passing in timezone-aware `datetime` is the only legit case:
    >>> obj = MyStrictModel.objects.create(my_datetime=my_aware_datetime)
    >>> print_iso_in_pacific_time(obj.my_datetime)
    2019-12-31 23:59:14.123456-08:00

Notice how the strict version is _much_ stricter w.r.t. the input values, making it much harder for a developer to (accidentally) get away with being lax about working with datetimes and Django's ORM.

If this sounds like it could be annoying, it sure is less annoying than having to fix a whole lot of database records after the fact, where perhaps some of the records are bad but not all.

There is a new settings parameter to monkey patch Django's `DateTimeField` to be strict:

* `STRICT_FIELDS_HARDEN_DJANGOS_DATETIMEFIELD = True`

This parameter is inspected when Django is launched and the field is monkey-patched to behave as desired.

*NOTE*: This requires that `'strict_fields'` be put in `settings.INSTALLED_APPS`, so that the monkey-patch functions are called on startup of Django.

*NOTE*: Monkey-patching is generally not considered good practice, as it may have unintended consequences. A read-through of :file:`strict_fields/apps.py` is highly recommended.

## Modifying all the problematic fields

There is one new settings parameter to monkey patch all of the problematic fields in order to make them strict:

* `STRICT_FIELDS_HARDEN_DJANGOS_FIELDS = True`

This parameter is inspected when Django is launched and the fields are monkey-patched to behave as desired.

*NOTE*: This requires that `'strict_fields'` be put in `settings.INSTALLED_APPS`, so that the monkey-patch functions are called on startup of Django.

*NOTE*: Monkey-patching is generally not considered good practice, as it may have unintended consequences. A read-through of :file:`strict_fields/apps.py` is highly recommended.

## Compatibility

`django-strict-fields` is compatible with Python 3.9 - 3.13 and Django 4.2 - 5.1.
