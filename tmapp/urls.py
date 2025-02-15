from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name ='index'),  
    # path('register', views.register, name ='register'),      
    path('registration', views.registration, name ='registration'),      
    path('login', views.login, name ='login'),   
    path('verify', views.verify, name ='verify'),   
    path('memb_dash', views.memb_dash, name ='memb_dash'),   
    path('memb_roles', views.memb_roles, name ='memb_roles'),   
    path('logout', views.logout, name ='logout'),   
    # path('post/<str:pk>', views.post, name ='post'),   
    
]