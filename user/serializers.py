from rest_framework import serializers

class ContactUsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(required=True)
    comment = serializers.CharField(required=True)