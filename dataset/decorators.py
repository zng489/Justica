import functools

from django.http import HttpResponseForbidden


def enable_disable_endpoint(enabled):
    def _enable_disable_endpoint(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if enabled:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Endpoint disabled")

        return wrapper

    return _enable_disable_endpoint
