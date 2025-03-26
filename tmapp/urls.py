from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),  
    path('registration/', views.registration, name='registration'),      
    path('login/', views.login_view, name='login'),   
    path('verify/', views.verify, name='verify'),

    # Member Dashboard Pages   
    path('memb_dash/', views.memb_dash, name='memb_dash'),   
    path('memb_roles/', views.memb_roles, name='memb_roles'),
    path('get-available-roles/<str:meeting_number>/', views.get_available_roles, name='get_available_roles'), 
    path('logout/', views.logout_view, name='logout'),  # Logout route   
    path('memb_membership/', views.memb_membership, name='memb_membership'),     
    path('check_payment_status/', views.check_payment_status, name='check_payment_status'),   
    path('update_payment_status/', views.update_payment_status, name='update_payment_status'),   
    # path('mpesa_callback/', views.mpesa_callback, name='mpesa_callback'),   
    path('memb_resources/', views.memb_resources, name='memb_resources'),   
    path('memb_notifications/', views.memb_notifications, name='memb_notifications'),   
    path('memb_elections/', views.memb_elections, name='memb_elections'),   
    path('memb_profile/', views.memb_profile, name='memb_profile'),   
    path('memb_settings/', views.memb_settings, name='memb_settings'),  
    path("update-profile-picture/", views.update_profile_picture, name="update_profile_picture"), 
    path('memb_contact/', views.memb_contact, name='memb_contact'),   
    path('memb_support/', views.memb_support, name='memb_support'),   
    # path('post/<str:pk>', views.post, name ='post'), 

    # Leader Dashboard  pages
    path('leader_login/', views.leader_login, name='leader_login'),
    path('leader_register/', views.leader_register, name='leader_register'),
    path('leader_dash/', views.leader_dash, name='leader_dash'),
    path('leader_membership/', views.leader_membership, name='leader_membership'),
    path("get_membership_data/", views.get_membership_data, name="get_membership_data"),
    path('leader_attendance/', views.leader_attendance, name='leader_attendance'),
    path('get_attendance/<str:meeting_number>/', views.get_attendance, name='get_attendance'),
    path('get_meeting_details/<str:meeting_number>/', views.get_meeting_details, name='get_meeting_details'),
    path('leader_elections/', views.leader_elections, name='leader_elections'),
]  

# Serve media files only in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


