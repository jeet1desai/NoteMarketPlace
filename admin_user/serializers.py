from rest_framework import serializers
from notes.models import SellerNotes

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