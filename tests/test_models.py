"""
Tests for actual use of the indexes after creating models with them.
"""
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from testapp.models import User, Room, RoomBooking, Job


class PartialIndexModelTest(TestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """

    def setUp(self):
        self.user1 = User.objects.create(name='User1')
        self.user2 = User.objects.create(name='User2')
        self.room1 = Room.objects.create(name='Room1')
        self.room2 = Room.objects.create(name='Room2')

    def test_roombooking_different_rooms(self):
        RoomBooking.objects.create(user=self.user1, room=self.room1)
        RoomBooking.objects.create(user=self.user1, room=self.room2)

    def test_roombooking_different_users(self):
        RoomBooking.objects.create(user=self.user1, room=self.room1)
        RoomBooking.objects.create(user=self.user2, room=self.room1)

    def test_roombooking_same_mark_first_deleted(self):
        for i in range(3):
            book = RoomBooking.objects.create(user=self.user1, room=self.room1)
            book.deleted_at = timezone.now()
            book.save()
        RoomBooking.objects.create(user=self.user1, room=self.room1)

    def test_roombooking_same_conflict(self):
        RoomBooking.objects.create(user=self.user1, room=self.room1)
        with self.assertRaises(IntegrityError):
            RoomBooking.objects.create(user=self.user1, room=self.room1)

    def test_job_same(self):
        now = timezone.now()
        job1 = Job.objects.create(created_at=now)
        job2 = Job.objects.create(created_at=now)
        self.assertEqual(job1.created_at, job2.created_at)
