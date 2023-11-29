# provide a way of serializing and deserializing the instances into representations such as json. 
# We can do this by declaring serializers that work very similar to Django's forms.
from rest_framework import serializers
from .models import User
from django.utils import timezone

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "password", "email", "is_email_verified", "role_id", "profile_picture", "is_active", "modified_date", "created_date"]
        # fields = '__all__'
        extra_kwargs = {'role_id': {'required': False}, 'created_date': {'required': False}}

    def validate(self, attrs):
        email_value = attrs.get("email")

        if User.objects.filter(email=email_value).exists():
            raise serializers.ValidationError("Email already exists.")

        return attrs
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('Password', None)
        return data
    
    def create(self, validated_data):
        validated_data['profile_picture'] = "https://img.freepik.com/premium-vector/man-avatar-profile-picture-vector-illustration_268834-538.jpg"
        user = User.objects.create(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email_value = attrs.get("email")
        password_value = attrs.get('password')

        if email_value and password_value:
            try:
                user = User.objects.get(email=email_value)
            except User.DoesNotExist:
                user = None
            if user is None:
                raise serializers.ValidationError('User not found.')
            elif user.password != password_value:
                raise serializers.ValidationError('Invalid credential')
            elif not user.is_active:
                raise serializers.ValidationError('User is not active.')
            elif not user.is_email_verified:
                raise serializers.ValidationError('Email verification is not done.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        return attrs
    
class VerifyEmailSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        id_user = attrs.get("user_id")
        try:
            user = User.objects.get(id=id_user)
        except User.DoesNotExist:
            user = None
        if user is None:
            raise serializers.ValidationError('User not found.')
        return attrs
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get('new_password')
        user = self.context.get("user")

        if old_password and new_password:
            user = User.objects.get(id=user.id)
            if user.password != old_password:
                raise serializers.ValidationError('Invalid credential')
        else:
            raise serializers.ValidationError('Must include "old_password" and "new_password".')
        return attrs
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user is None:
            raise serializers.ValidationError('User not found.')
        return attrs