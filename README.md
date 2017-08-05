# django-partial-index

PostgreSQL partial (sometimes also called filtered or conditional) index support for Django.

https://www.postgresql.org/docs/current/static/indexes-partial.html

## Install

`pip install django-partial-index`

Requires Django 1.11 or later.


## Usage

With `unique=True`, this can be used to create unique constraints for a subset of the rows.
For example, to enforce that each user can only have one non-deleted room booking at a time:

```python
from partial_index import PartialIndex

class RoomBooking(models.Model):
    user = models.ForeignKey(User)
    room = models.ForeignKey(Room)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        # unique_together = [('user', 'room')] - Does not allow multiple deleted rows. Instead use:
        indexes = [
            PartialIndex(fields=['user', 'room'], unique=True, where='deleted_at IS NULL')
        ]
```

With unique=False, partial indexes can be used to optimise lookups that return only a small subset of the rows.
For example, on a job queue table with millions of completed, and very few pending jobs, it can be used to
speed up a "find next pending job" query:

```python
from partial_index import PartialIndex

class Job(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

    class Meta:
        indexes = [
            PartialIndex(fields=['created_at'], unique=False, where='is_complete = false')
        ]
```

Of course, these (unique) indexes could be created by a handwritten [RunSQL migration](https://docs.djangoproject.com/en/1.11/ref/migration-operations/#runsql).
But the constraints are part of the business logic, and best kept close to the model definitions.


## TODOs

* Add tests.
* Test on Python versions older than 3.6.
* Add import and version checks to print nice errors when Django 1.11 is not installed.
* Replace `where='some sql expression'` with (Django's query expressions](https://docs.djangoproject.com/en/1.11/ref/models/expressions/) that are checked for valid syntax and field names.
* Add support for SQLite.
* Eventually make this package obsolete by getting it merged into Django's contrib.postgres module.
