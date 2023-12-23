from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from notemarketplace import renderers, utils
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from notemarketplace.decorators import admin_required, normal_required
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from notes.models import SellerNotes, Downloads, SellerNotesReportedIssues
from authenticate.models import User
from notes.serializers import NoteSerializer, DownloadSerializer
from .serializers import (UpdateStatusSerializer, UpdateStatusRemarkSerializer, AddSpamSerializer, SpamSerializer)
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
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
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
    @method_decorator(admin_required, name="published note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        notes = SellerNotes.objects.filter(status=4)
        
        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                notes = notes.filter(published_date__date=search_date.date())
            except ValueError:
                status_mapping = {'paid': True, 'Free': False}
                if search_param in status_mapping:
                    status_value = status_mapping[search_param]
                    notes = notes.filter(is_paid=status_value)
                else:   
                    notes = notes.filter(
                        Q(title__icontains=search_param) | Q(seller__first_name__icontains=search_param) |
                        Q(category__name__icontains=search_param) | Q(seller__last_name__icontains=search_param) |
                        Q(selling_price__icontains=search_param) | Q(actioned_by__last_name__icontains=search_param) |
                        Q(actioned_by__first_name__icontains=search_param)
                    )

        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        for note_data in serialized_in_progress_note:
            note_id = note_data['id']
            total_downloaded_notes_count = Downloads.objects.filter(note_id=note_id, is_attachment_downloaded=True).count()
            note_data['total_downloaded_notes'] = total_downloaded_notes_count

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


            if new_status == 5:
                utils.send_reject_note_mail(note_id, note_instance, note_instance.seller.email, remark)
            elif new_status == 6:
                utils.send_remove_note_mail(note_id, note_instance, note_instance.seller.email, remark)
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
        users = User.objects.filter(role_id=3, is_active=True)

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                users = users.filter(created_date__date=search_date.date())
            except ValueError:
                users = users.filter(
                    Q(first_name__icontains=search_param) | Q(last_name__icontains=search_param) | 
                    Q(email__icontains=search_param)     
                )

        serialized_user = UserProfileSerializer(users, many=True).data
        for user_data in serialized_user:
            user_id = user_data['id']
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
            total_selling_price = total_selling_price  or 0
            user_data['total_selling_price'] = total_selling_price or 0
            # total earning
            total_downloaded_notes_price = Downloads.objects.filter(seller_id=user_id, is_attachment_downloaded=True).aggregate(total=Sum('note__selling_price'))['total']
            total_downloaded_notes_price = total_downloaded_notes_price or 0
            user_data['total_earnings'] = total_downloaded_notes_price

        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
    
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="deactivate member")
    def delete(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id, role_id=3)
        except User.DoesNotExist:
            return Response({'status': status.HTTP_404_NOT_FOUND, 'msg': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = False
        user.save()

        published_notes = SellerNotes.objects.filter(seller=user, status=4)
        for note in published_notes:
            note.status = 6
            note.save()

        serialized_user = UserProfileSerializer(user).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)

class DownloadedNotes(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="downloaded notes")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        downloaded_notes = Downloads.objects.filter(is_attachment_downloaded=True)
        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                downloaded_notes = downloaded_notes.filter(attachment_downloaded_date__date=search_date.date())
            except ValueError:
                status_mapping = {'paid': True, 'free': False}
                if search_param in status_mapping:
                    status_value = status_mapping[search_param]
                    downloaded_notes = downloaded_notes.filter(note__is_paid=status_value)
                else:   
                    downloaded_notes = downloaded_notes.filter(
                        Q(note__title__icontains=search_param) | Q(seller__first_name__icontains=search_param) |
                        Q(note__category__name__icontains=search_param) | Q(seller__last_name__icontains=search_param) |
                        Q(downloader__first_name__icontains=search_param) | Q(downloader__first_name__icontains=search_param) |
                        Q(note__selling_price__icontains=search_param)
                    )
        serialized_downloaded_notes = DownloadSerializer(downloaded_notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_downloaded_notes}, status=status.HTTP_200_OK)

class RejectedNotes(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="rejected note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        notes = SellerNotes.objects.filter(status=5)

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                notes = notes.filter(modified_date__date=search_date.date())
            except ValueError:
                status_mapping = {'paid': True, 'free': False}
                if search_param in status_mapping:
                    status_value = status_mapping[search_param]
                    notes = notes.filter(is_paid=status_value)
                else:   
                    notes = notes.filter(
                        Q(title__icontains=search_param) | Q(seller__first_name__icontains=search_param) |
                        Q(category__name__icontains=search_param) | Q(seller__last_name__icontains=search_param) |
                        Q(admin_remark__icontains=search_param) | Q(actioned_by__last_name__icontains=search_param) |
                        Q(actioned_by__first_name__icontains=search_param)
                    )

        serialized_in_progress_note = NoteSerializer(notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_in_progress_note}, status=status.HTTP_200_OK)

class AllUserNotes(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="user notes")
    def get(self, request, user_id, format=None):
        user = User.objects.get(id=user_id)
        notes = SellerNotes.objects.filter(seller=user).exclude(status=1)
        serialized_user_notes = NoteSerializer(notes, many=True).data

        for note_data in serialized_user_notes:
            note_id = note_data['id']
            total_downloaded_notes_count = Downloads.objects.filter(note_id=note_id, is_attachment_downloaded=True).count()
            note_data['total_downloaded_notes'] = total_downloaded_notes_count
            note_data['total_earnings'] = total_downloaded_notes_count * note_data["selling_price"]

        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user_notes}, status=status.HTTP_200_OK)

class ReportSpam(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="add spam")
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = AddSpamSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            download_id = serializer.validated_data['download_id']
            remarks = serializer.validated_data['remarks']

            downloaded_note = Downloads.objects.get(id=download_id)
            note = SellerNotes.objects.get(id=downloaded_note.note.id)

            spam_note = SellerNotesReportedIssues.objects.create(
                remarks = remarks,
                note = note,
                reported_by = user,
                against_downloads = downloaded_note,
                created_date = timezone.now(),
                modified_date = timezone.now(),
                created_by = user,
                modified_by = user,
            )
            print(spam_note)
            serializer_spam_note = SpamSerializer(spam_note).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': 'Success', 'data': serializer_spam_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="get spams")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        spam_notes = SellerNotesReportedIssues.objects.filter(is_active=True)

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                spam_notes = spam_notes.filter(modified_date__date=search_date.date())
            except ValueError:
                spam_notes = spam_notes.filter(
                    Q(note__title__icontains=search_param) | Q(reported_by__first_name__icontains=search_param) |
                    Q(note__category__name__icontains=search_param) | Q(reported_by__last_name__icontains=search_param) |
                    Q(remarks__icontains=search_param) 
                )

        serialized_spam_notes = SpamSerializer(spam_notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_spam_notes}, status=status.HTTP_200_OK)
    
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="delete review")
    def delete(self, request, spam_id, format=None):
        try:
            spam = SellerNotesReportedIssues.objects.get(id=spam_id)
            spam.is_active = False
            spam.save()

            serializer_spam = SpamSerializer(spam).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': 'Success', 'data': serializer_spam}, status=status.HTTP_200_OK)
        except SellerNotesReportedIssues.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class Statistic(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="get stats")
    def get(self, request, format=None):
        stats={}
        notes = SellerNotes.objects.filter(status=3, is_active=True)
        stats['note_under_review'] = notes.count()

        last_seven_days = timezone.now() - timedelta(days=7)
        notes_downloaded_last_seven_days = Downloads.objects.filter(
            attachment_downloaded_date__gte=last_seven_days
        ).values('note').distinct()
        stats['note_downloaded'] = notes_downloaded_last_seven_days.count()

        new_member_registrations_last_seven_days = User.objects.filter(
            created_date__gte=last_seven_days
        ).count()
        stats['new_member'] = new_member_registrations_last_seven_days

        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': stats}, status=status.HTTP_200_OK)