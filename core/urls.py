from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),      
    path('home/', views.home, name='home'),       
    path('signup/', views.signup, name='signup'),    
    path('login/', views.login_view, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('post/', views.post_bai_viet, name='post_bai_viet'),
]
