from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.cache import cache_control

class CacheControlMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            return cache_control(no_cache=True, must_revalidate=True, no_store=True)(view_func)(request, *view_args, **view_kwargs)
