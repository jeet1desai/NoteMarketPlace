from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def super_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role_id == 1:
            return view_func(request, *args, **kwargs)
        else:
            return Response({ 'status': status.HTTP_403_FORBIDDEN, 'msg': "You don't have permission to access this API." }, status=status.HTTP_403_FORBIDDEN)

    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role_id in [1, 2]:
            return view_func(request, *args, **kwargs)
        else:
            return Response({ 'status': status.HTTP_403_FORBIDDEN, 'msg': "You don't have permission to access this API." }, status=status.HTTP_403_FORBIDDEN)
    return _wrapped_view

def normal_required(view_func):
    # @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.role_id in [1, 2, 3]:
            return view_func(request, *args, **kwargs)
        else:
            return Response({ 'status': status.HTTP_403_FORBIDDEN, 'msg': "You don't have permission to access this API." }, status=status.HTTP_403_FORBIDDEN)
    return _wrapped_view
