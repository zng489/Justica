from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin


class CheckURLExistsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        resolve(request.path)
