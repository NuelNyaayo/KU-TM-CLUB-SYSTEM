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
    # path('post/<str:pk>', views.post, name ='post'),   
]
