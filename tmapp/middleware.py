from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse  # Import reverse()

class LoginRequiredMiddleware:
    """Middleware to ensure users are authenticated before accessing protected pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that require authentication
        protected_paths = ['/memb_dash', '/memb_roles', '/memb_membership']

        # Paths that should NOT be protected (public access allowed)
        public_paths = ['/login', '/registration', '/verify', '/logout']

        # Check if request path starts with a protected path but is NOT in public paths
        if any(request.path.startswith(path) for path in protected_paths) and not request.user.is_authenticated:
            return redirect(reverse('login'))  # Use the name of your login URL

        return self.get_response(request)
