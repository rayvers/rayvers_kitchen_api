from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import UserProfile, UserAddress

from app.models import RestaurantWithdrawal

User = get_user_model()

class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        UserModel = get_user_model()

        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = UserModel.objects.get(email=email)
            except UserModel.DoesNotExist:
                raise serializers.ValidationError(_("No such user found with this email"))
            
            if not user.check_password(password):
                raise serializers.ValidationError(_("Incorrect password"))

            attrs['user'] = user
            attrs['password'] = password
            return attrs
        else:
            raise serializers.ValidationError(_("Must include 'email' and 'password'."))
        

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
            "last_login",
            "is_superuser",
            "role",
            "password",
            "code",
        ]

    def create(self, validated_data):
        # Hash the password before saving the user
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


# Serializer used to update the current user's address
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            "id",
            "user",
            "address",
            "street",
            "post_code",
            "apartment",
            "labelled_place",
        ]


class UserSerializerShort(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "is_active",
            "is_superuser",
            "password",
            "role"
        ]


class RestaurantWithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantWithdrawal
        fields = [
            'id',
            'account_bank',
            'account_number',
            'amount',
            'currency',
            'narration',
            'reference',
            'restaurant',
            'user',
        ]
