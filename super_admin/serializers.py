from rest_framework import serializers
from .models import SystemConfigurations, Country, NoteCategory, NoteType
from authenticate.models import User
from user.serializers import UserSerializer, CountrySerializer

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
        representation['phone_country_code'] = CountrySerializer(instance.phone_country_code).data
        return representation

class AdminPostSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_country_code = serializers.IntegerField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "password", "email", "is_email_verified", "role_id", "profile_picture", "is_active", "created_date", "phone_country_code", "phone_number"]
        extra_kwargs = {'password': {'required': False}}

    def validate(self, attrs):
        email_value = attrs.get("email")
        country_code_value = attrs.get("phone_country_code")

        if User.objects.filter(email=email_value).exists():
            raise serializers.ValidationError("Email already exists.")
        
        if not Country.objects.filter(id=country_code_value).exists():
            raise serializers.ValidationError("Country code not exists.")

        return attrs

class AdminPutSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_country_code = serializers.IntegerField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "password", "email", "is_email_verified", "role_id", "profile_picture", "is_active", "created_date", "phone_country_code", "phone_number"]
        extra_kwargs = {'password': {'required': False}}

    def validate(self, attrs):
        country_code_value = attrs.get("phone_country_code")
        if not Country.objects.filter(id=country_code_value).exists():
            raise serializers.ValidationError("Country code not exists.")
        return attrs

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

    def validate(self, attrs):
        country_name_value = attrs.get("name")
        country_code_value = attrs.get("code")
        
        if Country.objects.filter(code=country_code_value).exists():
            raise serializers.ValidationError("Country code is already exists.")
        if Country.objects.filter(name=country_name_value).exists():
            raise serializers.ValidationError("Country name is already exists.")
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation
    
class CountryPutSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    class Meta:
        model = Country
        fields = '__all__'
        extra_kwargs = {'created_by': {'required': False}, 'created_date': {'required': False}, 'modified_date': {'required': False}, 'modified_by': {'required': False}}

    def validate(self, attrs):
        country_name_value = attrs.get("name")
        country_code_value = attrs.get("code")
        country_id = self.instance.id

        if Country.objects.filter(code=country_code_value).exclude(id=country_id).exists():
            raise serializers.ValidationError("Country code is already exists.")
        if Country.objects.filter(name=country_name_value).exclude(id=country_id).exists():
            raise serializers.ValidationError("Country name is already exists.")
        return attrs

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