from django.urls import path, include
from . import views, group_views

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('upload', views.upload, name='upload'),
    path('follow', views.follow, name='follow'),
    path('search', views.search, name='search'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('like-post', views.like_post, name='like-post'),
    path('post/<uuid:post_id>/comment/', views.add_comment, name='add_comment'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('edit-post/<uuid:post_id>/', views.edit_post, name='edit-post'),
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete-post'),
    path('group/create/', group_views.create_group, name='create_group'),
    path('group/<uuid:group_id>/', group_views.group_detail, name='group_detail'),
    path('group/<uuid:group_id>/join/', group_views.join_group, name='join_group'),
    path('group/<uuid:group_id>/post/', group_views.create_group_post, name='create_group_post'),
    path('group/<uuid:group_id>/requests/', group_views.manage_group_requests, name='manage_group_requests'),
    path('group/request/<int:request_id>/handle/', group_views.handle_join_request, name='handle_join_request'),
    path('group/<uuid:group_id>/settings/', group_views.group_settings, name='group_settings'),
    path('group/<uuid:group_id>/update/', group_views.update_group, name='update_group'),
    path('group/<uuid:group_id>/member/<int:user_id>/remove/', group_views.remove_member, name='remove_member'),
    path('group/<uuid:group_id>/member/<int:user_id>/toggle-admin/', group_views.toggle_admin, name='toggle_admin'),
    path('group/post/<uuid:post_id>/like/', group_views.like_post, name='like_group_post'),
    path('group/post/<uuid:post_id>/comment/', group_views.add_comment, name='add_comment'),
    path('group/post/<uuid:post_id>/delete/', group_views.delete_post, name='delete_group_post'),
    path('messages/', views.messages_page, name='messages'),
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/<int:user_id>/', views.get_messages, name='get_messages'),
    
    # Marketplace URLs
    path('marketplace/', views.marketplace, name='marketplace'),
    path('create-listing/', views.create_listing, name='create_listing'),
    path('edit-product/<uuid:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<uuid:product_id>/', views.delete_product, name='delete_product'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('search-market/', views.search_market, name='search_market'),
    path('marketplace/product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('post/<str:post_id>/', views.post_detail, name='post_detail'),
    path('share-to-profile/<str:post_id>/', views.share_to_profile, name='share_to_profile'),
    path('group/<uuid:group_id>/chat/', views.group_chat, name='group_chat'),
    
    # Quiz URLs
    path('quiz/', include('quiz.urls')),
    path('quiz-home/', views.quiz_home, name='quiz_home'),  # Redirect to quiz app
]