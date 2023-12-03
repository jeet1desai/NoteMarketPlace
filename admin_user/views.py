from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from notemarketplace import renderers
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from notemarketplace.decorators import admin_required
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from notes.models import SellerNotes
from notes.serializers import NoteSerializer
from .serializers import (UpdateStatusSerializer, UpdateStatusRemarkSerializer)

class NoteUnderReview(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="note under review")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        notes = SellerNotes.objects.filter(status__in=[2, 3])

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d %H:%M")
                notes = notes.filter(created_date__date=search_date.date())
            except ValueError:
                status_mapping = {'submitted for review': 2, 'in review': 3}
                if search_param in status_mapping:
                    status_value = status_mapping[search_param]
                    notes = notes.filter(status=status_value)
                else:   
                    notes = notes.filter(
                        Q(title__icontains=search_param) | Q(seller__first_name__icontains=search_param) |
                        Q(category__name__icontains=search_param) | Q(seller__last_name__icontains=search_param)
                    )
        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class PublishedNotes(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="note under review")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        notes = SellerNotes.objects.filter(status=4)
        
        # if search_param:
        #     try:
        #         search_date = datetime.strptime(search_param, "%Y-%m-%d %H:%M")
        #         notes = notes.filter(created_date__date=search_date.date())
        #     except ValueError:
        #         status_mapping = {'submitted for review': 2, 'in review': 3}
        #         if search_param in status_mapping:
        #             status_value = status_mapping[search_param]
        #             notes = notes.filter(status=status_value)
        #         else:   
        #             notes = notes.filter(
        #                 Q(title__icontains=search_param) | Q(seller__first_name__icontains=search_param) |
        #                 Q(category__name__icontains=search_param) | Q(seller__last_name__icontains=search_param)
        #             )
        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class NoteUpdateStatus(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="note update status")
    def put(self, request, *args, **kwargs):
        serializer = UpdateStatusSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            new_status = serializer.validated_data['status']
            note_id = serializer.validated_data['note_id']
            note_instance = SellerNotes.objects.get(id=note_id)
            note_instance.status = new_status
            note_instance.actioned_by = user
            note_instance.modified_by = user
            note_instance.modified_date = timezone.now()
            if new_status == 4:
                note_instance.published_date = timezone.now()
            note_instance.save()
            serialized_note = NoteSerializer(note_instance).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class NoteUpdateRemarkStatus(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="reject note")
    def put(self, request, *args, **kwargs):
        serializer = UpdateStatusRemarkSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            remark = serializer.validated_data['remark']
            new_status = serializer.validated_data['status']
            note_id = serializer.validated_data['note_id']
            note_instance = SellerNotes.objects.get(id=note_id)
            note_instance.status = new_status
            note_instance.admin_remark = remark
            note_instance.actioned_by = user
            note_instance.modified_by = user
            note_instance.modified_date = timezone.now()
            note_instance.save()
            serialized_note = NoteSerializer(note_instance).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)
