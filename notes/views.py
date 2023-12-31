from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from notemarketplace import renderers, utils
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from notemarketplace.decorators import normal_required
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .serializers import (NotePostPutSerializer, NoteSerializer, CloneNoteSerializer, DownloadNoteSerializer,
    BuyerRequestSerializer, DownloadSerializer, AuthNoteSerializer)
from super_admin.models import Country, NoteCategory, NoteType
from .models import SellerNotes, Downloads, SellerNotesReviews, SellerNotesReportedIssues
from authenticate.models import User
from django.db.models import Q, Avg, Sum
from datetime import datetime
from super_admin.models import SystemConfigurations

class Note(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="create note")
    def post(self, request, uStatus, format=None):
        user = request.user
        serializer = NotePostPutSerializer(data=request.data)
        if serializer.is_valid():
            config = SystemConfigurations.objects.last()
            category = serializer.validated_data.pop('category')
            country = serializer.validated_data.pop('country')
            note_type = serializer.validated_data.pop('note_type')
            display_picture = serializer.validated_data.pop('display_picture')

            category_instance = NoteCategory.objects.get(id=int(category))
            country_instance = Country.objects.get(id=int(country)) if country != "" else None
            type_instance = NoteType.objects.get(id=int(note_type)) if note_type != "" else None

            if display_picture == "":
                serializer.validated_data['display_picture'] = config.note_picture
            else:
                serializer.validated_data['display_picture'] = display_picture
            
            serializer.validated_data['status'] = uStatus
            serializer.validated_data['category'] = category_instance
            serializer.validated_data['country'] = country_instance
            serializer.validated_data['note_type'] = type_instance
            serializer.validated_data['seller'] = user
            serializer.validated_data['created_by'] = user
            serializer.validated_data['modified_by'] = user
            serializer.validated_data['actioned_by'] = user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()

            note_instance = serializer.save()
            serialized_note = AuthNoteSerializer(note_instance).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_201_CREATED)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)
    
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="update note")
    def put(self, request, note_id, uStatus, format=None):
        user = request.user
        try:
            note = SellerNotes.objects.get(id=note_id, seller=user)
            serializer = NotePostPutSerializer(note, data=request.data)
            if serializer.is_valid():
                config = SystemConfigurations.objects.last()
                category = serializer.validated_data.pop('category')
                country = serializer.validated_data.pop('country')
                note_type = serializer.validated_data.pop('note_type')
                display_picture = serializer.validated_data.pop('display_picture')

                category_instance = NoteCategory.objects.get(id=int(category))
                country_instance = Country.objects.get(id=int(country)) if country != "" else None
                type_instance = NoteType.objects.get(id=int(note_type)) if note_type != "" else None

                if display_picture == "":
                    serializer.validated_data['display_picture'] = config.note_picture
                else:
                    serializer.validated_data['display_picture'] = display_picture
                
                serializer.validated_data['status'] = uStatus
                serializer.validated_data['category'] = category_instance
                serializer.validated_data['country'] = country_instance
                serializer.validated_data['note_type'] = type_instance
                serializer.validated_data['seller'] = user
                serializer.validated_data['modified_by'] = user
                serializer.validated_data['actioned_by'] = user
                serializer.validated_data['modified_date'] = timezone.now()

                note_instance = serializer.save()
                serialized_note = AuthNoteSerializer(note_instance).data
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
        notes = SellerNotes.objects.filter(status__in=[1, 2, 3], seller=user)

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

class DeleteNote(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="delete note")
    def delete(self, request, note_id, *args, **kwargs):
        user = request.user
        try:
            note = SellerNotes.objects.filter(id=note_id, status=1)
            note.delete()
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success" }, status=status.HTTP_200_OK)
        except SellerNotes.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class RejectedNote(ListAPIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="rejected note")
    def get(self, request, format=None):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user
        notes = SellerNotes.objects.filter(status=5, seller=user)

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
            
            if User.objects.filter(id=user.id, role_id__in=[1, 2]).exists():
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Successfully downloaded!', 'data': original_note.file}, status=status.HTTP_200_OK)
            if SellerNotes.objects.filter(id=note_id, seller=user).exists():
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Successfully downloaded!', 'data': original_note.file}, status=status.HTTP_200_OK)
            if Downloads.objects.filter(note__id=note_id, downloader=user, is_seller_has_allowed_to_download=True).exists():
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Successfully downloaded!', 'data': original_note.file}, status=status.HTTP_200_OK)
            elif Downloads.objects.filter(note__id=note_id, downloader=user, is_seller_has_allowed_to_download=False).exists():
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Seller will contact you."}, status=status.HTTP_200_OK)
            elif original_note.is_paid:
                download_note = Downloads.objects.create(
                    note=original_note,
                    created_by=user,
                    modified_by=user,
                    seller=seller_user,
                    downloader=user,
                    attachment_downloaded_date=timezone.now(),
                    is_attachment_downloaded=True,
                )
                utils.send_buyer_download_mail(user, seller_user, original_note)
                utils.send_seller_download_mail(seller_user, user, original_note)
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Seller will contact you.'}, status=status.HTTP_200_OK)
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
                return Response({ 'status': status.HTTP_200_OK, 'msg': 'Please check my download page', 'data': original_note.file }, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class BuyerRequests(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="buyer request")
    def get(self, request, *args, **kwargs):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user

        buyer_request_notes = Downloads.objects.filter(
            seller=user, note__is_paid=True,
            is_seller_has_allowed_to_download=False,
        )

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                buyer_request_notes = buyer_request_notes.filter(attachment_downloaded_date__date=search_date.date())
            except ValueError:
                sell_type_mapping = {'paid': False, 'free': True}
                if search_param in sell_type_mapping:
                    sell_type_value = sell_type_mapping[search_param]
                    buyer_request_notes = buyer_request_notes.filter(note__is_paid=sell_type_value)
                else:
                    buyer_request_notes = buyer_request_notes.filter(
                        Q(note__title__icontains=search_param) |
                        Q(attachment_downloaded_date__icontains=search_param) |
                        Q(note__category__name__icontains=search_param) |
                        Q(downloader__email__icontains=search_param) |
                        Q(downloader__phone_country_code__code__icontains=str(search_param)) |
                        Q(downloader__phone_number__icontains=str(search_param)) |
                        Q(note__selling_price__icontains=search_param)
                    )

        serialized_buyer_request = DownloadSerializer(buyer_request_notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_buyer_request}, status=status.HTTP_200_OK)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="buyer request update")
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = BuyerRequestSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            download_id = serializer.validated_data['download_id']

            note_instance = Downloads.objects.get(id=download_id)
            note_instance.is_seller_has_allowed_to_download = True
            note_instance.modified_by = user
            note_instance.modified_date = timezone.now()
            note_instance.save()

            utils.send_buyer_allow_download_mail(note_instance.downloader.email, user, note_instance.note)

            serialized_note = DownloadSerializer(note_instance).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class MySoldNotes(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="my sold note")
    def get(self, request, *args, **kwargs):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user

        my_sold_notes = Downloads.objects.filter(
            seller=user, is_seller_has_allowed_to_download=True,
        )

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                my_sold_notes = my_sold_notes.filter(attachment_downloaded_date__date=search_date.date())
            except ValueError:
                sell_type_mapping = {'paid': False, 'free': True}
                if search_param in sell_type_mapping:
                    sell_type_value = sell_type_mapping[search_param]
                    my_sold_notes = my_sold_notes.filter(note__is_paid=sell_type_value)
                else:
                    my_sold_notes = my_sold_notes.filter(
                        Q(note__title__icontains=search_param) |
                        Q(note__category__name__icontains=search_param) |
                        Q(downloader__email__icontains=search_param) |
                        Q(attachment_downloaded_date__icontains=search_param) |
                        Q(note__selling_price__icontains=search_param)
                    )

        serialized_sold_notes = DownloadSerializer(my_sold_notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_sold_notes}, status=status.HTTP_200_OK)

class MyDownloadNotes(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="my download note")
    def get(self, request, *args, **kwargs):
        search_param = request.query_params.get('search', '').lower()
        user = self.request.user

        my_download_notes = Downloads.objects.filter(
            downloader=user, is_seller_has_allowed_to_download=True,
        )

        if search_param:
            try:
                search_date = datetime.strptime(search_param, "%Y-%m-%d")
                my_download_notes = my_download_notes.filter(attachment_downloaded_date__date=search_date.date())
            except ValueError:
                sell_type_mapping = {'paid': False, 'free': True}
                if search_param in sell_type_mapping:
                    sell_type_value = sell_type_mapping[search_param]
                    my_download_notes = my_download_notes.filter(note__is_paid=sell_type_value)
                else:
                    my_download_notes = my_download_notes.filter(
                        Q(note__title__icontains=search_param) |
                        Q(note__category__name__icontains=search_param) |
                        Q(downloader__email__icontains=search_param) |
                        Q(attachment_downloaded_date__icontains=search_param) |
                        Q(note__selling_price__icontains=search_param)
                    )

        serialized_download_notes = DownloadSerializer(my_download_notes, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_download_notes}, status=status.HTTP_200_OK)

class NoteDetails(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def get(self, request, note_id, format=None):
        try:
            note_detail = SellerNotes.objects.get(id=note_id)
            serialized_note_detail = NoteSerializer(note_detail).data

            avg_rating = SellerNotesReviews.objects.filter(note=note_detail, is_active=True).aggregate(Avg('rating'))["rating__avg"]
            serialized_note_detail['avg_rating'] = round(avg_rating) if avg_rating else 0
            serialized_note_detail['rating_count'] = SellerNotesReviews.objects.filter(note=note_detail, is_active=True).count()
            serialized_note_detail['spam_count'] = SellerNotesReportedIssues.objects.filter(note=note_detail, is_active=True).count()

            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note_detail}, status=status.HTTP_200_OK)
        except SellerNotes.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
class AuthNoteDetails(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get auth note")
    def get(self, request, note_id, format=None):
        try:
            user = self.request.user
            note_detail = SellerNotes.objects.get(id=note_id, seller=user)
            serialized_note_detail = AuthNoteSerializer(note_detail).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note_detail}, status=status.HTTP_200_OK)
        except SellerNotes.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class Statistic(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get stats")
    def get(self, request, format=None):
        user = self.request.user
        stats={}
        buyer_request_notes = Downloads.objects.filter(seller=user, note__is_paid=True, is_seller_has_allowed_to_download=False)
        stats['buyer_request'] = buyer_request_notes.count()
        rejected_notes = SellerNotes.objects.filter(status=5, seller=user)
        stats['rejected_notes'] = rejected_notes.count()
        download_notes = Downloads.objects.filter(downloader=user, is_seller_has_allowed_to_download=True)
        stats['download_notes'] = download_notes.count()
        sold_notes = SellerNotes.objects.filter(downloads__is_attachment_downloaded=True, seller=user).distinct()
        stats['sold_notes'] = sold_notes.count()
        total_earnings = SellerNotes.objects.filter(downloads__is_attachment_downloaded=True, seller=user).aggregate(total=Sum('selling_price'))['total'] or 0
        stats['total_earnings'] = total_earnings

        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': stats}, status=status.HTTP_200_OK)
