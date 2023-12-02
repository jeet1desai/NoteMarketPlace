from rest_framework.views import APIView
from notemarketplace import renderers
from rest_framework.response import Response
from rest_framework import status
from super_admin.models import SystemConfigurations
from .serializers import ContactUsSerializer
from notemarketplace import utils

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