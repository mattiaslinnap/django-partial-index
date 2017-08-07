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

Set up a PartialIndex and insert it into your model's class-based Meta.indexes list:

```python
from partial_index import PartialIndex

class MyModel(models.Model):
    class Meta:
        indexes = [
            PartialIndex(fields=['user', 'room'], unique=True, where='deleted_at IS NULL'),
            PartialIndex(fields=['created_at'], unique=False, where_postgresql='is_complete = false', where_sqlite='is_complete = 0'),
        ]
```

Of course, these (unique) indexes could be created by a handwritten [RunSQL migration](https://docs.djangoproject.com/en/1.11/ref/migration-operations/#runsql).
But the constraints are part of the business logic, and best kept close to the model definitions.

### Partial unique constraints

With `unique=True`, this can be used to create unique constraints for a subset of the rows.

For example, you might have a model that has a deleted_at field to mark rows as archived instead of deleting them forever.
You wish to add unique constraints on "alive" rows, but allow multiple copies in the archive.
[Django's unique_together](https://docs.djangoproject.com/en/1.11/ref/models/options/#unique-together) is not sufficient here, as that cannot
distinguish between the archived and alive rows.

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

### Partial non-unique indexes

With `unique=False`, partial indexes can be used to optimise lookups that return only a small subset of the rows.

For example, you might have a job queue table which keeps an archive of millions of completed jobs. Among these are a few pending jobs,
which you want to find with a `.filter(is_complete=0)` query.

```python
from partial_index import PartialIndex

class Job(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.IntegerField(default=0)

    class Meta:
        indexes = [
            PartialIndex(fields=['created_at'], unique=False, where='is_complete = 0')
        ]
```

Compared to an usual full index on the `is_complete` field, this can be significantly smaller in disk and memory use, and faster to update.

### Different where-expressions for PostgreSQL and SQLite

Note that the where-expression is directly inserted into the `CREATE INDEX` sql statement, and must be valid for your database backend.

In rare cases, PostgreSQL and SQLite differ in the syntax that they expect. One such case is boolean literals:
SQLite only accepts numbers 0/1, and PostgreSQL only accepts unquoted false/true and a few quoted strings (but not numbers). You can provide
a separate where expression if you wish to support both backends in your project:

```python
from partial_index import PartialIndex

class Job(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)

    class Meta:
        indexes = [
            PartialIndex(fields=['created_at'], unique=False,
                         where_postgresql='is_complete = false',
                         where_sqlite='is_complete = 0')
        ]
```

If the expressions for both backends are the same, you must use the single `where=''` argument for consistency.

It is up to you to ensure that the expressions are otherwise valid SQL and have the same behaviour.

Using [Django's query expressions](https://docs.djangoproject.com/en/1.11/ref/models/expressions/) that check the syntax and generate valid SQL
for either database is planned for a future version.


## Version History

### 0.3.0 (latest)
* Add support for separate `where_postgresql=''` and `where_sqlite=''` predicates, when the expression has different syntax on the two
 database backends and you wish to support both.

### 0.2.1
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
