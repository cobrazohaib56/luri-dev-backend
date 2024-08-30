"""All the user serializers exists here."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()
from referrals.models import Referral


class UserSerializer(serializers.ModelSerializer):
    """Serializer to get user instance."""

    class Meta:
        """Exclude password when serializing users."""

        model = UserModel
        exclude = ["password"]

class UserListSerializer(serializers.ModelSerializer):
    """Serializer to get user instance."""
    referral_count = serializers.SerializerMethodField()

    class Meta:
        """Exclude password when serializing users."""

        model = UserModel
        fields = ["id", "first_name", "last_name", "email", "referral_count"]
    
    def get_referral_count(self, obj):
        return Referral.objects.filter(referrer=obj).count()

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer to register user."""
    referral_uuid = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        """Fields required when registering the user."""

        model = UserModel
        fields = ["id", "email", "first_name", "last_name", "password", "phone", "referral_uuid"]

