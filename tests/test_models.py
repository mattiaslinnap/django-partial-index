"""
Tests for actual use of the indexes after creating models with them.
"""
from django.db import IntegrityError
from django.test import TransactionTestCase
from django.utils import timezone

from testapp.models import User, Room, RoomBookingText, JobText, ComparisonText, RoomBookingQ, JobQ, ComparisonQ


class PartialIndexRoomBookingTest(TransactionTestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """

    def setUp(self):
        self.user1 = User.objects.create(name='User1')
        self.user2 = User.objects.create(name='User2')
        self.room1 = Room.objects.create(name='Room1')
        self.room2 = Room.objects.create(name='Room2')

    def test_roombooking_text_different_rooms(self):
        RoomBookingText.objects.create(user=self.user1, room=self.room1)
        RoomBookingText.objects.create(user=self.user1, room=self.room2)

    def test_roombooking_q_different_rooms(self):
        RoomBookingQ.objects.create(user=self.user1, room=self.room1)
        RoomBookingQ.objects.create(user=self.user1, room=self.room2)

    def test_roombooking_text_different_users(self):
        RoomBookingText.objects.create(user=self.user1, room=self.room1)
        RoomBookingText.objects.create(user=self.user2, room=self.room1)

    def test_roombooking_q_different_users(self):
        RoomBookingQ.objects.create(user=self.user1, room=self.room1)
        RoomBookingQ.objects.create(user=self.user2, room=self.room1)

    def test_roombooking_text_same_mark_first_deleted(self):
        for i in range(3):
            book = RoomBookingText.objects.create(user=self.user1, room=self.room1)
            book.deleted_at = timezone.now()
            book.save()
        RoomBookingText.objects.create(user=self.user1, room=self.room1)

    def test_roombooking_q_same_mark_first_deleted(self):
        for i in range(3):
            book = RoomBookingQ.objects.create(user=self.user1, room=self.room1)
            book.deleted_at = timezone.now()
            book.save()
        RoomBookingQ.objects.create(user=self.user1, room=self.room1)

    def test_roombooking_text_same_conflict(self):
        RoomBookingText.objects.create(user=self.user1, room=self.room1)
        with self.assertRaises(IntegrityError):
            RoomBookingText.objects.create(user=self.user1, room=self.room1)

    def test_roombooking_q_same_conflict(self):
        RoomBookingQ.objects.create(user=self.user1, room=self.room1)
        with self.assertRaises(IntegrityError):
            RoomBookingQ.objects.create(user=self.user1, room=self.room1)


class PartialIndexJobTest(TransactionTestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """
    def test_job_text_same_id(self):
        job1 = JobText.objects.create(order=1, group=1)
        job2 = JobText.objects.create(order=1, group=2)
        self.assertEqual(job1.order, job2.order)

    def test_job_q_same_id(self):
        job1 = JobQ.objects.create(order=1, group=1)
        job2 = JobQ.objects.create(order=1, group=2)
        self.assertEqual(job1.order, job2.order)

    def test_job_text_same_group(self):
        JobText.objects.create(order=1, group=1)
        with self.assertRaises(IntegrityError):
            JobText.objects.create(order=2, group=1)

    def test_job_q_same_group(self):
        JobQ.objects.create(order=1, group=1)
        with self.assertRaises(IntegrityError):
            JobQ.objects.create(order=2, group=1)

    def test_job_text_complete_same_group(self):
        job1 = JobText.objects.create(order=1, group=1, is_complete=True)
        job2 = JobText.objects.create(order=1, group=1)
        self.assertEqual(job1.order, job2.order)

    def test_job_q_complete_same_group(self):
        job1 = JobQ.objects.create(order=1, group=1, is_complete=True)
        job2 = JobQ.objects.create(order=1, group=1)
        self.assertEqual(job1.order, job2.order)

    def test_job_text_complete_later_same_group(self):
        job1 = JobText.objects.create(order=1, group=1)
        job2 = JobText.objects.create(order=1, group=1, is_complete=True)
        self.assertEqual(job1.order, job2.order)

    def test_job_q_complete_later_same_group(self):
        job1 = JobQ.objects.create(order=1, group=1)
        job2 = JobQ.objects.create(order=1, group=1, is_complete=True)
        self.assertEqual(job1.order, job2.order)


class PartialIndexComparisonTest(TransactionTestCase):
    """Test that partial unique constraints work as expected when inserting data to the db.

    Models and indexes are created when django creates the test db, they do not need to be set up.
    """
    def test_comparison_text_duplicate_same_number(self):
        ComparisonText.objects.create(a=1, b=1)
        with self.assertRaises(IntegrityError):
            ComparisonText.objects.create(a=1, b=1)

    def test_comparison_q_duplicate_same_number(self):
        ComparisonQ.objects.create(a=1, b=1)
        with self.assertRaises(IntegrityError):
            ComparisonQ.objects.create(a=1, b=1)

    def test_comparison_text_different_same_number(self):
        ComparisonText.objects.create(a=1, b=1)
        ComparisonText.objects.create(a=2, b=2)

    def test_comparison_q_different_same_number(self):
        ComparisonQ.objects.create(a=1, b=1)
        ComparisonQ.objects.create(a=2, b=2)

    def test_comparison_text_duplicate_different_numbers(self):
        ComparisonText.objects.create(a=1, b=2)
        ComparisonText.objects.create(a=1, b=2)

    def test_comparison_q_duplicate_different_numbers(self):
        ComparisonQ.objects.create(a=1, b=2)
        ComparisonQ.objects.create(a=1, b=2)
