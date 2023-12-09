from rest_framework.views import APIView
from notemarketplace import renderers
from rest_framework.response import Response
from rest_framework import status
from super_admin.models import SystemConfigurations
from .serializers import (ContactUsSerializer, CountrySerializer, CategorySerializer, NoteTypeSerializer,
                          UserProfileSerializer, UserProfileUpdateSerializer, AdminProfileUpdateSerializer,
                          AddReviewSerializer, ReviewSerializer)
from notemarketplace import utils
from rest_framework.permissions import IsAuthenticated
from notemarketplace.decorators import normal_required, admin_required
from django.utils.decorators import method_decorator
from super_admin.models import Country, NoteCategory, NoteType
from authenticate.models import User
from django.utils import timezone
from notes.models import Downloads, SellerNotes, SellerNotesReviews

class ContactUs(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def post(self, request, format=None):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            last_row = SystemConfigurations.objects.last()
            if last_row is None:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': "Error" }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data = {
                    'email': last_row.email,
                    'full_name': request.data.get('name'),
                    'user_email': request.data.get('email'),
                    'subject': request.data.get('subject'),
                    'comment': request.data.get('comment'),
                }
                utils.send_contact_us_mail(data)
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': data }, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

class NoteCategoryList(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get category list")
    def get(self, request, format=None):
        all_category = NoteCategory.objects.filter(is_active=True)
        serialized_category = CategorySerializer(all_category, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)
    
class NoteTypeList(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get type list")
    def get(self, request, format=None):
        all_type = NoteType.objects.filter(is_active=True)
        serialized_type = NoteTypeSerializer(all_type, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_type}, status=status.HTTP_200_OK)
    
class CountryList(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get country list")
    def get(self, request, format=None):
        all_country = Country.objects.filter(is_active=True)
        serialized_country = CountrySerializer(all_country, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
    
class ProfileDetails(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get profile details")
    def get(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id)
            serialized_user = UserProfileSerializer(user).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class UserProfileUpdate(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="update user profile")
    def put(self, request, format=None):
        try:
            user = User.objects.get(id=request.user.id)
            serializer = UserProfileUpdateSerializer(user, data=request.data, context={'user':user})
            if serializer.is_valid():
                country_code = serializer.validated_data.pop('phone_country_code')
                country = serializer.validated_data.pop('country')

                country_code_instance = Country.objects.get(id=int(country_code)) if country_code != "" else None
                country_instance = Country.objects.get(id=int(country))

                serializer.validated_data['modified_date'] = timezone.now()
                serializer.validated_data['modified_by'] = user
                serializer.validated_data['phone_country_code'] = country_code_instance
                serializer.validated_data['country'] = country_instance

                updated_user = serializer.save()
                serialized_user = UserProfileSerializer(updated_user).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class AdminProfileUpdate(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="update admin profile")
    def put(self, request, format=None):
        try:
            user = User.objects.get(id=request.user.id)
            serializer = AdminProfileUpdateSerializer(user, data=request.data, context={'user':user})
            if serializer.is_valid():
                country_code = serializer.validated_data.pop('phone_country_code')

                country_code_instance = Country.objects.get(id=int(country_code)) if country_code != "" else None

                serializer.validated_data['modified_date'] = timezone.now()
                serializer.validated_data['modified_by'] = user
                serializer.validated_data['phone_country_code'] = country_code_instance

                updated_user = serializer.save()
                serialized_user = UserProfileSerializer(updated_user).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class Review(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="add review")
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = AddReviewSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            download_id = serializer.validated_data['download_id']
            rating = serializer.validated_data['rating']
            comment = serializer.validated_data['comment']

            downloaded_note = Downloads.objects.get(id=download_id)
            note = SellerNotes.objects.get(id=downloaded_note.note.id)

            review = SellerNotesReviews.objects.create(
                rating = rating,
                comment = comment,
                note = note,
                reviewed_by = user,
                against_downloads = downloaded_note,
                created_date = timezone.now(),
                modified_date = timezone.now(),
                created_by = user,
                modified_by = user,
            )
            serializer_review = ReviewSerializer(review).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': 'Success', 'data': serializer_review}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': serializer.errors}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(normal_required, name="get review")
    def get(self, request, note_id, format=None):
        note = SellerNotes.objects.get(id=note_id)
        reviews = SellerNotesReviews.objects.filter(note=note, is_active=True)

        serialized_note_review = ReviewSerializer(reviews, many=True).data
        return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_note_review}, status=status.HTTP_200_OK)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="delete review")
    def delete(self, request, review_id, format=None):
        try:
            review = SellerNotesReviews.objects.get(id=review_id)
            review.is_active = False
            review.save()

            serializer_review = ReviewSerializer(review).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': 'Success', 'data': serializer_review}, status=status.HTTP_200_OK)
        except SellerNotesReviews.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        
