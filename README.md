# django-partial-index

[![Build Status](https://api.travis-ci.org/mattiaslinnap/django-partial-index.svg?branch=master)](https://travis-ci.org/mattiaslinnap/django-partial-index)

Partial (sometimes also called filtered or conditional) index support for Django.

With partial indexes, only some subset of the rows in the table have corresponding index entries.
This can be useful for optimizing index size and query speed, and to add unique constraints for only selected rows.

More info on partial indexes:

* https://www.postgresql.org/docs/current/static/indexes-partial.html
* https://sqlite.org/partialindex.html


## Install

`pip install django-partial-index`

Requirements:

* Django 1.11 or later.
* PostgreSQL or SQLite database backend. (Partial indexes are not supported on MySQL, and require major hackery on Oracle.)
* Python 2.7 and 3.4 - 3.6. (All Python versions supported by Django 1.11.)

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

With `unique=False`, partial indexes can be used to optimise lookups that return only a small subset of the rows.
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

Note that the where-expression is directly inserted into the `CREATE INDEX` sql statement, and must be valid for your database backend.
This means that you would have to use `where='is_complete = false'` on PostgreSQL and `where='is_complete = 0'` on SQLite for the Job model.
Using [Django's query expressions](https://docs.djangoproject.com/en/1.11/ref/models/expressions/) that check the syntax and generate valid SQL
for either database is planned for a future version.

Of course, these (unique) indexes could be created by a handwritten [RunSQL migration](https://docs.djangoproject.com/en/1.11/ref/migration-operations/#runsql).
But the constraints are part of the business logic, and best kept close to the model definitions.

## Version History

## 0.2.1 (latest)
* Ensure that automatically generated index names depend on the "unique" and "where" parameters. Otherwise two indexes with the same fields would be considered identical by Django.

### 0.2.0
* Fully tested SQLite and PostgreSQL support.
* Tests for generated SQL statements, adding and removing indexes, and that unique constraints work when inserting rows into the db tables.
* Python 2.7, 3.4-3.6 support.

### 0.1.1
* Experimental SQLite support.

### 0.1.0
* First release, working but untested PostgreSQL support.

## Future plans

* Replace `where='some sql expression'` with [Django's query expressions](https://docs.djangoproject.com/en/1.11/ref/models/expressions/) that are checked for valid syntax and field names.
* Eventually make this package obsolete by getting it merged into Django's contrib.postgres module.
