from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='manage_users'),
    path('posts/', views.manage_posts, name='manage_posts'),
    path('groups/', views.manage_groups, name='manage_groups'),
    path('users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('groups/toggle/<uuid:group_id>/', views.toggle_group_status, name='toggle_group_status'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('posts/delete/<uuid:post_id>/', views.delete_post, name='delete_post'),
    path('groups/delete/<uuid:group_id>/', views.delete_group, name='delete_group'),
] 