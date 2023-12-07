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
from notes.models import SellerNotes, Downloads
from authenticate.models import User
from notes.serializers import NoteSerializer
from .serializers import (UpdateStatusSerializer, UpdateStatusRemarkSerializer)
from user.serializers import UserProfileSerializer
from django.db.models import Sum

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

class Members(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="members")
    def get(self, request, *args, **kwargs): 
        search_param = request.query_params.get('search', '').lower()
        notes = User.objects.filter(role_id=3, is_active=True)
        serialized_user = UserProfileSerializer(notes, many=True).data

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                notes = notes.filter(created_date__date=search_date.date())
            except ValueError:
                notes = notes.filter(
                    Q(first_name__icontains=search_param) | Q(last_name__icontains=search_param) | 
                    Q(email__icontains=search_param)     
                )

        for user_data in serialized_user:
            user_id = user_data['id']
            # note user review
            notes_under_review_count = SellerNotes.objects.filter(seller_id=user_id, status=3).count()
            user_data['notes_under_review'] = notes_under_review_count
            # note published
            notes_published_count = SellerNotes.objects.filter(seller_id=user_id, status=4).count()
            user_data['notes_published_notes'] = notes_published_count
            # note downloaded
            total_downloaded_notes_count = Downloads.objects.filter(seller_id=user_id, is_attachment_downloaded=True).count()
            user_data['total_downloaded_notes'] = total_downloaded_notes_count
            # total expense
            total_selling_price = SellerNotes.objects.filter(seller_id=user_id, status=4).aggregate(total=Sum('selling_price'))['total']
            user_data['total_selling_price'] = total_selling_price or 0
            # total earning
            total_downloaded_notes_price = Downloads.objects.filter(seller_id=user_id, is_attachment_downloaded=True).aggregate(total=Sum('note__selling_price'))['total']
            total_downloaded_notes_price = total_downloaded_notes_price or 0
            total_earnings = total_selling_price + total_downloaded_notes_price
            user_data['total_earnings'] = total_earnings

        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
