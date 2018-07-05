"""
Tests for actual use of the indexes after creating models with them.
"""
import datetime
from unittest import skip

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from testapp.serializers import RoomBookingAllFieldsSerializer, RoomBookingNoConditionFieldSerializer, RoomBookingJustRoomSerializer, RoomBookingTextSerializer
from testapp.models import User, Room, RoomBookingQ


@skip
class OnlyQTestCase(TestCase):
    def test_text_condition_improperlyconfigured(self):
        ser = RoomBookingTextSerializer(data={'user': 1, 'room': 1})
        with self.assertRaises(ImproperlyConfigured):
            ser.is_valid()


class SerializerTestCase(object):
    """Base class for serializer tests. Does not inherit from TestCase so that it would not run by itself.
    Subclasses must inherit from TestCase, and set serializerclass property.
    """
    serializerclass = None
    conflict_error = 'RoomBookingQ with the same values for room, user already exists.'

    def setUp(self):
        self.user1 = User.objects.create(name='User1')
        self.user2 = User.objects.create(name='User2')
        self.room1 = Room.objects.create(name='Room1')
        self.room2 = Room.objects.create(name='Room2')
        self.booking1 = RoomBookingQ.objects.create(user=self.user1, room=self.room1)
        self.booking2 = RoomBookingQ.objects.create(user=self.user1, room=self.room2)

    def test_add_duplicate_invalid(self):
        if self.serializerclass != RoomBookingJustRoomSerializer:
            ser = self.serializerclass(data={'user': self.user1.id, 'room': self.room1.id})
            self.assertFalse(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
            self.assertIn(self.conflict_error, ser.errors['__all__'])
        else:
            pass  # Skipped - JustRoomSerializer only works for modifications.

    def test_add_duplicate_when_deleted_valid(self):
        if self.serializerclass != RoomBookingJustRoomSerializer:
            self.booking1.deleted_at = datetime.datetime.utcnow()
            self.booking1.save()

            ser= self.serializerclass(data={'user': self.user1.id, 'room': self.room1.id})
            self.assertTrue(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
            self.assertFalse(ser.errors)
        else:
            pass  # Skipped - JustRoomSerializer only works for modifications.

    def test_add_non_duplicate_valid(self):
        if self.serializerclass != RoomBookingJustRoomSerializer:
            ser= self.serializerclass(data={'user': self.user2.id, 'room': self.room1.id})
            self.assertTrue(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
            self.assertFalse(ser.errors)
        else:
            pass  # Skipped - JustRoomSerializer only works for modifications.

    def test_modify_existing_valid(self):
        ser= self.serializerclass(data={'user': self.user1.id, 'room': self.room1.id}, instance=self.booking1)
        self.assertTrue(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
        self.assertFalse(ser.errors)

    def test_modify_another_to_be_duplicate_invalid(self):
        ser= self.serializerclass(data={'user': self.user1.id, 'room': self.room1.id}, instance=self.booking2)
        self.assertFalse(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
        self.assertIn(self.conflict_error, ser.errors['__all__'])

    def test_modify_another_to_be_duplicate_when_deleted_valid(self):
        self.booking1.deleted_at = datetime.datetime.utcnow()
        self.booking1.save()

        ser= self.serializerclass(data={'user': self.user1.id, 'room': self.room1.id}, instance=self.booking2)
        self.assertTrue(ser.is_valid(), 'Serializer errors: %s' % ser.errors)
        self.assertFalse(ser.errors)


@skip
class AllFieldsSerializerTest(SerializerTestCase, TestCase):
    """Test that partial unique validation on a ModelSerializer works when all fields are present on the serializer."""
    serializerclass = RoomBookingAllFieldsSerializer


@skip
class NoConditionFieldSerializerTest(SerializerTestCase, TestCase):
    """Test that partial unique validation on a ModelSerializer works when all index fields, but not the condition field are present on the serializer."""
    serializerclass = RoomBookingNoConditionFieldSerializer


@skip
class SingleFieldSerializerTest(SerializerTestCase, TestCase):
    """Test that partial unique validation on a ModelSerializer works when not all unique fields are present on the serializer.

    These have to be provided from an existing instance.
    """
    serializerclass = RoomBookingJustRoomSerializer
