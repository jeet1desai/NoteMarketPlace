from rest_framework import renderers
from rest_framework import status

import json 

class ResponseRenderer(renderers.JSONRenderer):
    charset='utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response=''
        if 'ErrorDetail' in str(data):
            response = json.dumps({ 'status': status.HTTP_400_BAD_REQUEST, 'data': data, 'msg': "Error" })
        else:
            response = json.dumps(data)
        return response