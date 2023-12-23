from rest_framework import serializers
from notes.models import SellerNotes, Downloads, SellerNotesReportedIssues
from user.serializers import UserSerializer
from notes.serializers import NoteSerializer

class UpdateStatusSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(required=True)
    status = serializers.IntegerField(required=True)

    def validate(self, attrs):
        note_id = attrs.get("note_id")

        if not SellerNotes.objects.filter(id=note_id, is_active=True).exists():
            raise serializers.ValidationError("Note is not exists.")
        return attrs
    
class UpdateStatusRemarkSerializer(serializers.Serializer):
    note_id = serializers.IntegerField(required=True)
    status = serializers.IntegerField(required=True)
    remark = serializers.CharField(required=True)

    def validate(self, attrs):
        note_id = attrs.get("note_id")

        if not SellerNotes.objects.filter(id=note_id, is_active=True).exists():
            raise serializers.ValidationError("Note is not exists.")
        return attrs

class SpamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerNotesReportedIssues
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        representation['reported_by'] = UserSerializer(instance.reported_by).data
        representation['note'] = NoteSerializer(instance.note).data
        return representation
    
class AddSpamSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=True)
    download_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        download_id = attrs.get("download_id")
        user = self.context.get("user")

        if not Downloads.objects.filter(id=download_id, downloader=user, is_seller_has_allowed_to_download=True).exists():
            raise serializers.ValidationError("Note is not exist on your download.")
        if SellerNotesReportedIssues.objects.filter(against_downloads__id=download_id, reported_by=user).exists():
            raise serializers.ValidationError("Your have added against this note.")
        return attrs