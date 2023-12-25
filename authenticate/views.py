from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, VerifyEmailSerializer, LoginSerializer, ChangePasswordSerializer, ResetPasswordSerializer
from rest_framework import status
from notemarketplace import utils, renderers
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import random
import string
from notemarketplace.decorators import normal_required
from django.utils.decorators import method_decorator
from super_admin.models import SystemConfigurations

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
class Register(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            config = SystemConfigurations.objects.last()
            serializer.validated_data['profile_picture'] = config.profile_picture
            # Create the user
            user = serializer.save()
            serialized_user = RegisterSerializer(user).data
            # Send mail
            utils.send_email_verification_mail(serialized_user["id"], serialized_user["email"])
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
        return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
    
class Login(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_value = serializer.data.get("email")
            user = User.objects.get(email=email_value)
            serialized_user = RegisterSerializer(user).data

            token = get_tokens_for_user(user)

            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user, 'token': token}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmail(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def get(self, request, user_id):
        serializer = VerifyEmailSerializer(data={ 'user_id': user_id })
        if serializer.is_valid():
            user = User.objects.get(id=user_id)
            user.is_email_verified = True
            user.save()
            serialized_user = RegisterSerializer(user).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [renderers.ResponseRenderer]
    @method_decorator(normal_required, name="change password")
    def post(self, request, format=None):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            new_password = serializer.data.get("new_password")
            user.password = new_password
            user.save()
            serialized_user = RegisterSerializer(user).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPassword(APIView):
    renderer_classes = [renderers.ResponseRenderer]
    def post(self, request, format=None):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            user = User.objects.get(email=email)
            
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            user.password = new_password
            user.save()

            utils.send_reset_password_mail(new_password, user.email)

            serialized_user = RegisterSerializer(user).data
            return Response({ 'status': status.HTTP_200_OK, 'msg': "Success", 'data': serialized_user}, status=status.HTTP_200_OK)
        else:
            return Response({ 'status': status.HTTP_400_BAD_REQUEST, 'msg': serializer.errors }, status=status.HTTP_400_BAD_REQUEST)
   



