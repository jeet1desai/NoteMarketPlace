from rest_framework.pagination import PageNumberPagination
import math
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
      
    def get_paginated_response(self, data):
        if self.request.query_params.get('page_size'):
            self.page_size = int(self.request.query_params.get('page_size'))

        total_page = math.ceil(self.page.paginator.count / self.page_size)
        return {
            'count': self.page.paginator.count,
            'total': total_page,
            'page_size': self.page_size,
            'current': self.page.number,
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
        }
    
    def get_next_link(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()
    
    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()