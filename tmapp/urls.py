from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  
    path('registration/', views.registration, name='registration'),      
    path('login/', views.login_view, name='login'),   
    path('verify/', views.verify, name='verify'),   
    path('memb_dash/', views.memb_dash, name='memb_dash'),   
    path('memb_roles/', views.memb_roles, name='memb_roles'), 
    path('logout/', views.logout_view, name='logout'),  # Logout route   
    path('memb_membership/', views.memb_membership, name='memb_membership'),   
    path('memb_resources/', views.memb_resources, name='memb_resources'),   
    path('memb_notifications/', views.memb_notifications, name='memb_notifications'),   
    path('memb_elections/', views.memb_elections, name='memb_elections'),   
    path('memb_profile/', views.memb_profile, name='memb_profile'),   
    path('memb_settings/', views.memb_settings, name='memb_settings'),   
    path('memb_contact/', views.memb_contact, name='memb_contact'),   
    path('memb_support/', views.memb_support, name='memb_support'),   
    # path('post/<str:pk>', views.post, name ='post'), 

    # Leader Dashboard  

    path('leader_login/', views.leader_login, name='leader_login'),
    path('leader_register/', views.leader_register, name='leader_register'),
    path('leader_dash/', views.leader_dash, name='leader_dash'),
    path('leader_membership/', views.leader_membership, name='leader_membership'),
    # path('memb_support/', views.memb_support, name='memb_support'),
    # path('memb_support/', views.memb_support, name='memb_support'),
]
