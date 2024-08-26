from django.http import HttpResponse
from django.test import RequestFactory

from dataset.decorators import enable_disable_endpoint


class TestEnableDisableEndpoint:
    def test_view_enabled(self):
        def dummy_view(request, *args, **kwargs):
            return HttpResponse()

        factory = RequestFactory()
        request = factory.get("/path/")

        decorated_view = enable_disable_endpoint(enabled=True)(dummy_view)
        response = decorated_view(request)

        assert response.status_code == 200

    def test_view_disabled(self):
        def dummy_view(request, *args, **kwargs):
            return HttpResponse()

        factory = RequestFactory()
        request = factory.get("/path/")

        decorated_view = enable_disable_endpoint(enabled=False)(dummy_view)
        response = decorated_view(request)

        assert response.status_code == 403
