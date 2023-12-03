from rest_framework.views import APIView
from notemarketplace import renderers
from rest_framework.response import Response
from rest_framework import status
from super_admin.models import SystemConfigurations
from .serializers import (ContactUsSerializer, CountrySerializer, CategorySerializer, NoteTypeSerializer,
                          UserProfileSerializer)
from notemarketplace import utils
from rest_framework.permissions import IsAuthenticated
from notemarketplace.decorators import normal_required
from django.utils.decorators import method_decorator
from super_admin.models import Country, NoteCategory, NoteType
from authenticate.models import User

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
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success" }, status=status.HTTP_200_OK)
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

    

