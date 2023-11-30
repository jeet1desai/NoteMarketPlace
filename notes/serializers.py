from rest_framework import serializers
from .models import SellerNotes
from super_admin.models import Country, NoteCategory, NoteType
from super_admin.serializers import UserSerializer, CountrySerializer, NoteTypeSerializer, CategorySerializer

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerNotes
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        if instance.country:
            representation['country'] = CountrySerializer(instance.country).data
        if instance.note_type:
           representation['note_type'] = NoteTypeSerializer(instance.note_type).data
        if instance.category:
            representation['category'] = CategorySerializer(instance.category).data
        representation['seller'] = UserSerializer(instance.seller).data
        representation['actioned_by'] = UserSerializer(instance.actioned_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

class NotePostPutSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    notes_preview = serializers.CharField(required=True)
    file = serializers.CharField(required=True)
    file_name = serializers.CharField(required=True)
    file_size = serializers.IntegerField(required=True)
    is_paid = serializers.BooleanField(required=True)
    selling_price = serializers.IntegerField(required=True)
    note_type = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    number_of_pages = serializers.IntegerField()
    university_name = serializers.CharField()
    course = serializers.CharField()
    course_code = serializers.CharField()
    professor = serializers.CharField()

    class Meta:
        model = SellerNotes
        fields = "__all__"
        extra_kwargs = {'created_by': {'required': False}, 'modified_by': {'required': False}, 'seller': {'required': False},  'actioned_by': {'required': False}}

    def validate(self, attrs):
        category = attrs.get("category")
        note_type = attrs.get("note_type")
        country = attrs.get("country")

        if not NoteCategory.objects.filter(id=int(category)).exists():
            raise serializers.ValidationError("Note category is not exists.")
        if note_type != "" and not NoteType.objects.filter(id=int(note_type)).exists():
            raise serializers.ValidationError("Note type is not exists.")
        if country != "" and not Country.objects.filter(id=int(country)).exists():
            raise serializers.ValidationError("Country is not exists.")
        return attrs