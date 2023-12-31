from rest_framework.views import APIView
from notemarketplace import renderers
from .models import SystemConfigurations, Country, NoteCategory, NoteType
from authenticate.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import (ConfigSerializer, AdminGetSerializer, CategoryPostSerializer,
    CountryGetSerializer, CategoryGetSerializer, TypeGetSerializer, CountryPostSerializer, TypePostSerializer, 
    AdminPostSerializer, AdminPutSerializer, CountryPutSerializer)
from notemarketplace.decorators import super_admin_required, admin_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime
from notemarketplace import utils
import secrets
import string
from django.db.models import Q

# Config
class GetConfiguration(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def get(self, request, format=None):
        last_row = SystemConfigurations.objects.last()
        if last_row is None:
           empty_config = {'email': '','phone_number': '', 'facebook_url': '', 'twitter_url': '', 'linkedIn_url': '', 'profile_picture': '', 'note_picture': ''}
           return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': empty_config}, status=status.HTTP_200_OK)
        else:
            serialized_config = ConfigSerializer(last_row).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_config}, status=status.HTTP_200_OK)
    
class PostConfiguration(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(super_admin_required, name="post config")
    def post(self, request, format=None):
        serializer = ConfigSerializer(data=request.data)
        if serializer.is_valid():
            profile_picture = serializer.validated_data.pop('profile_picture')
            note_picture = serializer.validated_data.pop('note_picture')

            if profile_picture == "":
                serializer.validated_data['profile_picture'] = "https://img.freepik.com/premium-vector/man-avatar-profile-picture-vector-illustration_268834-538.jpg"
            else:
                serializer.validated_data['profile_picture'] = profile_picture

            if note_picture == "":
                serializer.validated_data['note_picture'] = "https://shorturl.at/orBVW"
            else:
                serializer.validated_data['note_picture'] = note_picture

            serializer.validated_data['created_by'] = request.user
            config = serializer.save()
            serialized_config = ConfigSerializer(config).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_config}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

# Admin
class Admin(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(super_admin_required, name="get admin")
    def get(self, request, admin_id=None, format=None):
        if admin_id is not None:
            # Get a single row logic
            try:
                admin = User.objects.get(id=admin_id, role_id=2)
                serialized_admin = AdminGetSerializer(admin).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_admin}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get all rows logic
            search_param = request.query_params.get('search', '').lower()
            all_admins = User.objects.filter(role_id=2)

            if search_param:
                try:
                    search_date = datetime.strptime(search_param, "%Y-%m-%d")
                    all_admins = all_admins.filter(created_date__date=search_date.date())
                except ValueError:  
                    all_admins = all_admins.filter(
                        Q(first_name__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(last_name__icontains=search_param) | Q(email__icontains=search_param) | 
                        Q(phone_number__icontains=search_param)
                    )
            
            serialized_admins = AdminGetSerializer(all_admins, many=True).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_admins}, status=status.HTTP_200_OK)
        
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(super_admin_required, name="post admin")
    def post(self, request, format=None):
        serializer = AdminPostSerializer(data=request.data)
        if serializer.is_valid():
            config = SystemConfigurations.objects.last()
            phone_country_code = serializer.validated_data.pop('phone_country_code')
            country_instance = Country.objects.get(id=phone_country_code)

            random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

            serializer.validated_data['phone_country_code'] = country_instance
            serializer.validated_data['profile_picture'] = config.profile_picture
            serializer.validated_data['created_by'] = request.user
            serializer.validated_data['modified_by'] = request.user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()
            serializer.validated_data['role_id'] = 2
            serializer.validated_data['password'] = random_password

            user_instance = serializer.save()
            serialized_admin = AdminGetSerializer(user_instance).data

            utils.send_welcome_mail(random_password, serialized_admin["email"])
            utils.send_email_verification_mail(serialized_admin["id"], serialized_admin["email"])

            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_admin}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(super_admin_required, name="update country")
    def put(self, request, admin_id, format=None):
        try:
            admin = User.objects.get(id=admin_id)
            serializer = AdminPutSerializer(admin, data=request.data)
            if serializer.is_valid():
                phone_country_code = serializer.validated_data.pop('phone_country_code')
                country_instance = Country.objects.get(id=phone_country_code)

                serializer.validated_data['phone_country_code'] = country_instance
                serializer.validated_data['modified_by'] = request.user
                serializer.validated_data['modified_date'] = timezone.now()
                admin_save = serializer.save()

                serialized_admin = AdminGetSerializer(admin_save).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_admin}, status=status.HTTP_200_OK)
            else:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(super_admin_required, name="delete admin")
    def delete(self, request, admin_id, format=None):
        try:
            admin = User.objects.get(id=admin_id)
            admin.is_active = False
            admin.modified_by = request.user
            admin.modified_date = timezone.now()
            admin.save()

            serialized_country = AdminGetSerializer(admin).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

# Country
class Countries(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="get country")
    def get(self, request, country_id=None, format=None):
        if country_id is not None:
            try:
                country = Country.objects.get(id=country_id)
                serialized_country = CountryGetSerializer(country).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
            except Country.DoesNotExist:
                return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            search_param = request.query_params.get('search', '').lower()
            all_countries = Country.objects.all()

            if search_param:
                try:
                    search_date = datetime.strptime(search_param, "%Y-%m-%d")
                    all_countries = all_countries.filter(created_date__date=search_date.date())
                except ValueError:  
                    all_countries = all_countries.filter(
                        Q(name__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(code__icontains=search_param) | Q(created_by__first_name__icontains=search_param) | 
                        Q(created_by__last_name__icontains=search_param)
                    )
            
            serialized_countries = CountryGetSerializer(all_countries, many=True).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_countries}, status=status.HTTP_200_OK)
    
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="post country")
    def post(self, request, format=None):
        serializer = CountryPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['created_by'] = request.user
            serializer.validated_data['modified_by'] = request.user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()
            country = serializer.save()

            serialized_country = CountryPostSerializer(country).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="update country")
    def put(self, request, country_id, format=None):
        try:
            country = Country.objects.get(id=country_id)
            serializer = CountryPutSerializer(country, data=request.data)
            if serializer.is_valid():
                serializer.validated_data['modified_by'] = request.user
                serializer.validated_data['modified_date'] = timezone.now()
                country = serializer.save()

                serialized_country = CountryPutSerializer(country).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
            else:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="delete country")
    def delete(self, request, country_id, format=None):
        try:
            country = Country.objects.get(id=country_id)
            country.is_active = False
            country.modified_by = request.user
            country.modified_date = timezone.now()
            country.save()

            serialized_country = CountryGetSerializer(country).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_country}, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

# Note Category
class NoteCategories(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="get note category")
    def get(self, request, category_id=None, format=None):
        if category_id is not None:
            try:
                category = NoteCategory.objects.get(id=category_id)
                serialized_category = CategoryGetSerializer(category).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)
            except NoteCategory.DoesNotExist:
                return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Error"}, status=status.HTTP_404_NOT_FOUND)
        else:
            search_param = request.query_params.get('search', '').lower()
            all_category = NoteCategory.objects.all()

            if search_param:
                try:
                    search_date = datetime.strptime(search_param, "%Y-%m-%d")
                    all_category = all_category.filter(created_date__date=search_date.date())
                except ValueError:  
                    all_category = all_category.filter(
                        Q(name__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(description__icontains=search_param) | Q(created_by__first_name__icontains=search_param) | 
                        Q(created_by__last_name__icontains=search_param)
                    )
                                
            serialized_category = CategoryGetSerializer(all_category, many=True).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="post category")
    def post(self, request, format=None):
        serializer = CategoryPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['created_by'] = request.user
            serializer.validated_data['modified_by'] = request.user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()
            category = serializer.save()

            serialized_category = CategoryPostSerializer(category).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="update category")
    def put(self, request, category_id, format=None):
        try:
            category = NoteCategory.objects.get(id=category_id)
            serializer = CategoryPostSerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.validated_data['modified_by'] = request.user
                serializer.validated_data['modified_date'] = timezone.now()
                category_save = serializer.save()

                serialized_category = CategoryPostSerializer(category_save).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)
            else:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="delete category")
    def delete(self, request, category_id, format=None):
        try:
            category = NoteCategory.objects.get(id=category_id)
            category.is_active = False
            category.modified_by = request.user
            category.modified_date = timezone.now()
            category.save()

            serialized_category = CategoryGetSerializer(category).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_category}, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

# Note Type
class NoteTypes(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="get note type")
    def get(self, request, type_id=None, format=None):
        if type_id is not None:
            try:
                type = NoteType.objects.get(id=type_id)
                serialized_type = TypeGetSerializer(type).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_type}, status=status.HTTP_200_OK)
            except NoteType.DoesNotExist:
                return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Error"}, status=status.HTTP_404_NOT_FOUND)
        else:
            search_param = request.query_params.get('search', '').lower()
            all_types = NoteType.objects.all()

            if search_param:
                try:
                    search_date = datetime.strptime(search_param, "%Y-%m-%d")
                    all_types = all_types.filter(created_date__date=search_date.date())
                except ValueError:  
                    all_types = all_types.filter(
                        Q(name__icontains=search_param) | Q(created_date__icontains=search_param) |
                        Q(description__icontains=search_param) | Q(created_by__first_name__icontains=search_param) | 
                        Q(created_by__last_name__icontains=search_param)
                    )
            
            serialized_types = TypeGetSerializer(all_types, many=True).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_types}, status=status.HTTP_200_OK)
 
    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="post type")
    def post(self, request, format=None):
        serializer = TypePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['created_by'] = request.user
            serializer.validated_data['modified_by'] = request.user
            serializer.validated_data['created_date'] = timezone.now()
            serializer.validated_data['modified_date'] = timezone.now()
            type = serializer.save()

            serialized_type = TypePostSerializer(type).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_type}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="update type")
    def put(self, request, type_id, format=None):
        try:
            type = NoteType.objects.get(id=type_id)
            serializer = TypePostSerializer(type, data=request.data)
            if serializer.is_valid():
                serializer.validated_data['modified_by'] = request.user
                serializer.validated_data['modified_date'] = timezone.now()
                type_save = serializer.save()

                serialized_type = TypePostSerializer(type_save).data
                return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_type}, status=status.HTTP_200_OK)
            else:
                return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)

    renderer_classes = [renderers.ResponseRenderer]
    permission_classes = [IsAuthenticated]
    @method_decorator(admin_required, name="delete type")
    def delete(self, request, type_id, format=None):
        try:
            type = NoteType.objects.get(id=type_id)
            type.is_active = False
            type.modified_by = request.user
            type.modified_date = timezone.now()
            type.save()

            serialized_type = TypeGetSerializer(type).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_type}, status=status.HTTP_200_OK)
        except Country.DoesNotExist:
            return Response({ 'status': status.HTTP_404_NOT_FOUND, 'msg': "Not Found"}, status=status.HTTP_404_NOT_FOUND)
