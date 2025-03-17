from django.shortcuts import redirect
from django.urls import reverse  # Import reverse()

class MemberLoginRequiredMiddleware:
    """Middleware to ensure only authenticated members can access member pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # **Member pages that require authentication**
        protected_paths = [
            '/memb_dash', '/memb_roles', '/memb_membership', '/memb_resources',
            '/memb_notifications', '/memb_elections', '/memb_profile', 
            '/memb_settings', '/memb_contact', '/memb_support'
        ]

        # **Public pages (accessible without authentication)**
        public_paths = ['/login', '/registration', '/verify', '/logout']

        # **Redirect unauthenticated users trying to access protected member pages**
        if any(request.path.startswith(path) for path in protected_paths) and not request.user.is_authenticated:
            return redirect(reverse('login'))  # Redirect to normal login

        return self.get_response(request)


class LeaderLoginRequiredMiddleware:
    """Middleware to ensure only authenticated leaders can access leader dashboard pages."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # **Leader dashboard pages that require authentication**
        protected_paths = ['/leader_dash', '/leader_membership', '/leader_attendance', '/leader_elections']

        # **Public leader pages that don't require authentication**
        public_paths = ['/leader_login', '/leader_register', '/verify', '/logout']

        # **Redirect unauthenticated users trying to access leader pages**
        if any(request.path.startswith(path) for path in protected_paths) and not request.user.is_authenticated:
            return redirect(reverse('leader_login'))  # Redirect to leader login

        return self.get_response(request)
