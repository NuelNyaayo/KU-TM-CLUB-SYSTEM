from django.urls import path, include
from . import views

auth_patterns = [
    path('registration/', views.registration, name='registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify/', views.verify, name='verify'),
]

member_patterns = [
    path('dashboard/', views.memb_dash, name='memb_dash'),
    path('roles/', views.memb_roles, name='memb_roles'),
    path('membership/', views.memb_membership, name='memb_membership'),
    path('resources/', views.memb_resources, name='memb_resources'),
    path('notifications/', views.memb_notifications, name='memb_notifications'),
    path('elections/', views.memb_elections, name='memb_elections'),
    path('profile/', views.memb_profile, name='memb_profile'),
    path('settings/', views.memb_settings, name='memb_settings'),
    path('contact/', views.memb_contact, name='memb_contact'),
    path('support/', views.memb_support, name='memb_support'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', include((auth_patterns, 'auth'))),
    path('member/', include((member_patterns, 'member'))),
]
