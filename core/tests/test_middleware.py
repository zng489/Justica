from unittest import mock

import pytest
from django.urls import reverse
from django.urls.exceptions import Resolver404

from core.middleware import CheckURLExistsMiddleware


class TestCheckURLExists:
    def test_url_exists(self):
        m_request = mock.Mock(path=reverse("core:main"))
        middleware = CheckURLExistsMiddleware(None)
        middleware.process_request(m_request)

    def test_url_do_not_exists(self):
        m_request = mock.Mock(path="/dot-no-exists")
        middleware = CheckURLExistsMiddleware(None)

        with pytest.raises(Resolver404):
            middleware.process_request(m_request)
