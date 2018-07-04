"""Models for tests."""

from django.db import models
from django.db.models import F


from partial_index import PartialIndex, PQ, ValidatePartialUniqueMixin


class AB(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)


class ABC(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)
    c = models.CharField(max_length=50)


class User(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RoomBookingText(ValidatePartialUniqueMixin, models.Model):
    """Note that ValidatePartialUniqueMixin cannot actually be used on this model, as it uses text-based index conditions.

    Any ModelForm or DRF Serializer validation will fail.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where='deleted_at IS NULL')]


class RoomBookingQ(ValidatePartialUniqueMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where=PQ(deleted_at__isnull=True))]


class JobText(models.Model):
    order = models.IntegerField()
    group = models.IntegerField()
    is_complete = models.BooleanField(default=False)

    class Meta:
        indexes = [
            PartialIndex(fields=['-order'], unique=False, where_postgresql='is_complete = false', where_sqlite='is_complete = 0'),
            PartialIndex(fields=['group'], unique=True, where_postgresql='is_complete = false', where_sqlite='is_complete = 0'),
        ]


class JobQ(models.Model):
    order = models.IntegerField()
    group = models.IntegerField()
    is_complete = models.BooleanField(default=False)

    class Meta:
        indexes = [
            PartialIndex(fields=['-order'], unique=False, where=PQ(is_complete=False)),
            PartialIndex(fields=['group'], unique=True, where=PQ(is_complete=False)),
        ]


class ComparisonText(models.Model):
    """Partial index that references multiple fields on the model."""
    a = models.IntegerField()
    b = models.IntegerField()

    class Meta:
        indexes = [
            PartialIndex(fields=['a', 'b'], unique=True, where='a = b'),
        ]


class ComparisonQ(models.Model):
    """Partial index that references multiple fields on the model."""
    a = models.IntegerField()
    b = models.IntegerField()

    class Meta:
        indexes = [
            PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a=F('b'))),
        ]
