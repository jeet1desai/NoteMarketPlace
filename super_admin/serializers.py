from rest_framework import serializers
from .models import SystemConfigurations, Country, NoteCategory, NoteType
from authenticate.models import User

# User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]

# Config
class ConfigGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfigurations
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        return representation

class ConfigPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfigurations
        fields = '__all__'
        extra_kwargs = {'created_by': {'required': False}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        return representation

# Admin
class AdminGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "phone_country_code", "phone_number", "created_date", "created_by", "is_active"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        return representation

# Country
class CountryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation
    
class CountryPostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    class Meta:
        model = Country
        fields = '__all__'
        extra_kwargs = {'created_by': {'required': False}, 'created_date': {'required': False}, 'modified_date': {'required': False}, 'modified_by': {'required': False}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

# Note Category
class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteCategory
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

class CategoryPostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    class Meta:
        model = NoteCategory
        fields = '__all__'
        extra_kwargs = {'created_by': {'required': False}, 'created_date': {'required': False}, 'modified_date': {'required': False}, 'modified_by': {'required': False}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

# Note Type
class TypeGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteType
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

class TypePostSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    class Meta:
        model = NoteType
        fields = '__all__'
        extra_kwargs = {'created_by': {'required': False}, 'created_date': {'required': False}, 'modified_date': {'required': False}, 'modified_by': {'required': False}}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation