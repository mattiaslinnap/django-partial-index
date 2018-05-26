from django.db import models
from django.db.models import Q, F

from partial_index import PartialIndex


class AB(models.Model):
    a = models.CharField(max_length=50)
    b = models.CharField(max_length=50)


class User(models.Model):
    name = models.CharField(max_length=50)


class Room(models.Model):
    name = models.CharField(max_length=50)


class RoomBookingText(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where='deleted_at IS NULL')]


class RoomBookingQ(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where=Q(deleted_at__isnull=True))]


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
            PartialIndex(fields=['-order'], unique=False, where=Q(is_complete=False)),
            PartialIndex(fields=['group'], unique=True, where=Q(is_complete=False)),
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
            PartialIndex(fields=['a', 'b'], unique=True, where=Q(a=F('b'))),
        ]
