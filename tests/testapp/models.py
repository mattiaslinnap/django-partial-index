from django.db import models

from partial_index import PartialIndex


class User(models.Model):
    name = models.CharField(max_length=50)


class Room(models.Model):
    name = models.CharField(max_length=50)


class RoomBooking(models.Model):
    user = models.ForeignKey(User)
    room = models.ForeignKey(Room)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [PartialIndex(fields=['user', 'room'], unique=True, where='deleted_at IS NULL')]


class Job(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # Using IntegerField instead of BooleanField in the test, since PostgreSQL and SQLite have different boolean literals.
    # In real projects it is your job to use a where='' expression that is valid for your selected database backend.
    is_complete = models.IntegerField(default=0)

    class Meta:
        indexes = [PartialIndex(fields=['-created_at'], unique=False, where='is_complete = 0')]
