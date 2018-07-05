from rest_framework import serializers

from testapp.models import RoomBookingText, RoomBookingQ


class RoomBookingTextSerializer(serializers.ModelSerializer):
    """Always fails with ImproperlyConfigured error, because mixin cannot be used with text-based conditions."""
    class Meta:
        model = RoomBookingText
        fields = ('user', 'room', 'deleted_at')


class RoomBookingAllFieldsSerializer(serializers.ModelSerializer):
    """All fields are present on the form."""
    class Meta:
        model = RoomBookingQ
        fields = ('user', 'room', 'deleted_at')


class RoomBookingNoConditionFieldSerializer(serializers.ModelSerializer):
    """Index fields are present on the form, but the condition field is not."""
    class Meta:
        model = RoomBookingQ
        fields = ('user', 'room')


class RoomBookingJustRoomSerializer(serializers.ModelSerializer):
    """Only one out of the two indexed fields is present on the form."""
    class Meta:
        model = RoomBookingQ
        fields = ('room', )
