from rest_framework import serializers
from .models import SellerNotes, Downloads, SellerNotesReviews
from super_admin.models import Country, NoteCategory, NoteType
from user.serializers import CategorySerializer, NoteTypeSerializer, CountrySerializer, UserSerializer

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerNotes
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        seller = instance.seller
        user = self.context.get("user")
        if seller != user and user.role_id == 3:
            representation.pop('file', None)
        if instance.country:
            representation['country'] = CountrySerializer(instance.country).data
        if instance.note_type:
           representation['note_type'] = NoteTypeSerializer(instance.note_type).data
        if instance.category:
            representation['category'] = CategorySerializer(instance.category).data
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['seller'] = UserSerializer(instance.seller).data
        representation['actioned_by'] = UserSerializer(instance.actioned_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation

class NotePostPutSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    display_picture = serializers.CharField(allow_blank=True)
    notes_preview = serializers.CharField(required=True)
    file = serializers.CharField(required=True)
    file_name = serializers.CharField(required=True)
    file_size = serializers.IntegerField(required=True)
    is_paid = serializers.BooleanField(required=True)
    selling_price = serializers.IntegerField(required=True)
    note_type = serializers.CharField(allow_blank=True)
    country = serializers.CharField(allow_blank=True)
    number_of_pages = serializers.IntegerField()
    university_name = serializers.CharField(allow_blank=True)
    course = serializers.CharField(allow_blank=True)
    course_code = serializers.CharField(allow_blank=True)
    professor = serializers.CharField(allow_blank=True)

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
    
class CloneNoteSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        note_id = attrs.get("note_id")

        if not SellerNotes.objects.filter(id=note_id).exists():
            raise serializers.ValidationError("Note is not exists.")
        if not SellerNotes.objects.filter(id=note_id, status=5).exists():
            raise serializers.ValidationError("Note is not in rejected state.")
        return attrs
    
class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Downloads
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get("user")
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['note'] = NoteSerializer(instance.note, context={'user': user}).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        representation['seller'] = UserSerializer(instance.seller).data
        representation['downloader'] = UserSerializer(instance.downloader).data
        return representation

class DownloadNoteSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        note_id = attrs.get("note_id")
        user = self.context.get("user")

        if not SellerNotes.objects.filter(id=note_id).exists():
            raise serializers.ValidationError("Note is not exists.")
        if SellerNotes.objects.filter(id=note_id, seller=user).exists():
            raise serializers.ValidationError("You cannot download your own note.")
        if Downloads.objects.filter(note_id=note_id, downloader=user).exists():
            raise serializers.ValidationError("You have already purchased it.")
        return attrs

class BuyerRequestSerializer(serializers.Serializer):
    download_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        download_id = attrs.get("download_id")
        user = self.context.get("user")

        if not Downloads.objects.filter(id=download_id, seller=user).exists():
            raise serializers.ValidationError("Request not exist.")
        return attrs