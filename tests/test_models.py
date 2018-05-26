"""
Tests for actual use of the indexes after creating models with them.
"""
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from testapp.models import User, Room, RoomBooking, Job, Comparison


class PartialIndexRoomBookingTest(TestCase):
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


class PartialIndexJobTest(TestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """
    def test_job_same_id(self):
        job1 = Job.objects.create(order=1, group=1)
        job2 = Job.objects.create(order=1, group=2)
        self.assertEqual(job1.order, job2.order)

    def test_job_same_group(self):
        Job.objects.create(order=1, group=1)
        with self.assertRaises(IntegrityError):
            Job.objects.create(order=2, group=1)

    def test_job_complete_same_group(self):
        job1 = Job.objects.create(order=1, group=1, is_complete=True)
        job2 = Job.objects.create(order=1, group=1)
        self.assertEqual(job1.order, job2.order)

    def test_job_complete_later_same_group(self):
        job1 = Job.objects.create(order=1, group=1)
        job2 = Job.objects.create(order=1, group=1, is_complete=True)
        self.assertEqual(job1.order, job2.order)


class PartialIndexComparisonTest(TestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """
    def test_comp_duplicate_same_number(self):
        Comparison.objects.create(a=1, b=1)
        with self.assertRaises(IntegrityError):
            Comparison.objects.create(a=1, b=1)

    def test_comp_different_same_number(self):
        Comparison.objects.create(a=1, b=1)
        Comparison.objects.create(a=2, b=2)

    def test_comp_duplicate_different_numbers(self):
        Comparison.objects.create(a=1, b=2)
        Comparison.objects.create(a=1, b=2)
