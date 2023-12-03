from rest_framework import serializers
from super_admin.models import Country, NoteCategory, NoteType
from authenticate.models import User

class ContactUsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(required=True)
    comment = serializers.CharField(required=True)

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteCategory
        fields = ["id", "name", "description"]

class NoteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteType
        fields = ["id", "name", "description"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name"]