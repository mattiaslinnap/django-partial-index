"""Models for tests."""

from django.db import models
from django.db.models import F


from partial_index import PartialIndex, PQ


class User(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class RoomBookingQ(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where=PQ(deleted_at__isnull=True))]


class JobQ(models.Model):
    order = models.IntegerField()
    group = models.IntegerField()
    is_complete = models.BooleanField(default=False)

    class Meta:
        indexes = [
            PartialIndex(fields=['-order'], unique=False, where=PQ(is_complete=False)),
            PartialIndex(fields=['group'], unique=True, where=PQ(is_complete=False)),
        ]


class ComparisonQ(models.Model):
    """Partial index that references multiple fields on the model."""
    a = models.IntegerField()
    b = models.IntegerField()

    class Meta:
        indexes = [
            PartialIndex(fields=['a', 'b'], unique=True, where=PQ(a=F('b'))),
        ]
