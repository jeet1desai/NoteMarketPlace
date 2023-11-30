from rest_framework.views import APIView
from notemarketplace import renderers
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from notemarketplace.decorators import normal_required
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import (NotePostPutSerializer, NoteSerializer)
from super_admin.models import Country, NoteCategory, NoteType

# Create your views here.
class Note(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="create note")
    def post(self, request, format=None):
        serializer = NotePostPutSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.pop('category')
            country = serializer.validated_data.pop('country')
            note_type = serializer.validated_data.pop('note_type')
            display_picture = serializer.validated_data.pop('display_picture')

            category_instance = NoteCategory.objects.get(id=int(category))
            country_instance = Country.objects.get(id=int(country)) if country != "" else None
            type_instance = NoteType.objects.get(id=int(note_type)) if note_type != "" else None

            if "display_picture" not in serializer.validated_data or display_picture == "":
                serializer.validated_data['display_picture'] = "https://img.freepik.com/premium-vector/man-avatar-profile-picture-vector-illustration_268834-538.jpg"
            else:
                serializer.validated_data['display_picture'] = display_picture
            
            serializer.validated_data['category'] = category_instance
            serializer.validated_data['country'] = country_instance
            serializer.validated_data['note_type'] = type_instance
            serializer.validated_data['seller'] = request.user
            serializer.validated_data['created_by'] = request.user
            serializer.validated_data['modified_by'] = request.user
            serializer.validated_data['actioned_by'] = request.user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()

            note_instance = serializer.save()
            serialized_note = NoteSerializer(note_instance).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)
    




