from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from notemarketplace import renderers, utils
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from notemarketplace.decorators import normal_required
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import (NotePostPutSerializer, NoteSerializer, CloneNoteSerializer, DownloadNoteSerializer)
from super_admin.models import Country, NoteCategory, NoteType
from .models import SellerNotes, Downloads
from authenticate.models import User
from django.db.models import Q
from datetime import datetime

class Note(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="create note")
    def post(self, request, uStatus, format=None):
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
            
            serializer.validated_data['status'] = uStatus
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
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_201_CREATED)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)
    
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="update note")
    def put(self, request, note_id, uStatus, format=None):
        try:
            note = SellerNotes.objects.get(id=note_id)
            serializer = NotePostPutSerializer(note, data=request.data)
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
                
                serializer.validated_data['status'] = uStatus
                serializer.validated_data['category'] = category_instance
                serializer.validated_data['country'] = country_instance
                serializer.validated_data['note_type'] = type_instance
                serializer.validated_data['seller'] = request.user
                serializer.validated_data['modified_by'] = request.user
                serializer.validated_data['actioned_by'] = request.user
                serializer.validated_data['modified_date'] = timezone.now()

                note_instance = serializer.save()
                serialized_note = NoteSerializer(note_instance).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_200_OK)
            else:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        except SellerNotes.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class InProgressNote(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="in progress note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user
        notes = SellerNotes.objects.filter(status__in=[1, 2, 3], created_by=user)

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                notes = notes.filter(created_date__date=search_date.date())
            except ValueError:
                status_mapping = {'draft': 1, 'submitted': 2, 'in review': 3}
                if search_param in status_mapping:
                    status_value = status_mapping[search_param]
                    notes = notes.filter(status=status_value)
                else:   
                    notes = notes.filter(
                        Q(title__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(category__name__icontains=search_param)
                    )
        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class PublishedNote(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="published note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user
        notes = SellerNotes.objects.filter(status=4, created_by=user)

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                notes = notes.filter(created_date__date=search_date.date())
            except ValueError:
                sell_type_mapping = { 'paid': False, 'free': True }
                if search_param in sell_type_mapping:
                    sell_type_value = sell_type_mapping[search_param]
                    notes = notes.filter(is_paid=sell_type_value)
                else:   
                    notes = notes.filter(
                        Q(title__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(category__name__icontains=search_param)
                    )
        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class RejectedNote(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="rejected note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user
        notes = SellerNotes.objects.filter(status=5, created_by=user)

        if search_param:
            notes = notes.filter(
                Q(title__icontains=search_param) | Q(admin_remark__icontains=search_param) |
                Q(category__name__icontains=search_param)
            )
        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class CloneNoteView(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="clone note")
    def post(self, request, *args, **kwargs):
        serializer = CloneNoteSerializer(data=request.data)
        if serializer.is_valid():
            note_id = serializer.validated_data['note_id']
            original_note = SellerNotes.objects.get(id=note_id)
            
            cloned_note = SellerNotes.objects.create(
                title=original_note.title,
                description=original_note.description,
                status=1,
                display_picture=original_note.display_picture,
                notes_preview=original_note.notes_preview,
                file_name=original_note.file_name,
                file=original_note.file,
                file_size=original_note.file_size,
                category=original_note.category,
                created_date=original_note.created_date,
                created_by=original_note.created_by,
                actioned_by=original_note.actioned_by,
                modified_by=original_note.modified_by,
                seller=original_note.seller,
            )
            serializer_note = NoteSerializer(cloned_note).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serializer_note }, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)
        
class DownloadNote(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="download note")
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = DownloadNoteSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            note_id = serializer.validated_data['note_id']
            original_note = SellerNotes.objects.get(id=note_id)
            seller_user = User.objects.get(id=original_note.created_by.id)
            if original_note.is_paid:
                download_note = Downloads.objects.create(
                    note=original_note,
                    created_by=user,
                    modified_by=user,
                    seller=seller_user,
                    downloader=user
                )
                utils.send_buyer_download_mail(user, seller_user, original_note)
                utils.send_seller_download_mail(seller_user, user, original_note)
                serializer_download_note = DownloadNoteSerializer(download_note).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Please check my download page', 'data': serializer_download_note}, status=status.HTTP_200_OK)
            else:
                download_note = Downloads.objects.create(
                    is_seller_has_allowed_to_download=True,
                    is_attachment_downloaded=True,
                    attachment_downloaded_date=timezone.now(),
                    note=original_note,
                    created_by=user,
                    modified_by=user,
                    seller=seller_user,
                    downloader=user
                )
                serializer_download_note = DownloadNoteSerializer(download_note).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Seller will contact you.', 'data': serializer_download_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)






