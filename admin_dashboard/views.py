from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from core.models import Profile, Post, Group
from .models import AdminLog
from django.db.models import Count, Q
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin, login_url='signin')
def admin_dashboard(request):
    # Thống kê cơ bản
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    locked_users = User.objects.filter(is_active=False).count()
    total_posts = Post.objects.count()
    total_groups = Group.objects.count()
    locked_groups = Group.objects.filter(is_locked=True).count()
    
    # Người dùng mới nhất
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Bài viết mới nhất
    recent_posts = Post.objects.order_by('-created_at')[:5]
    
    # Nhóm hoạt động nhiều nhất
    active_groups = Group.objects.annotate(
        post_count=Count('grouppost')
    ).order_by('-post_count')[:5]
    
    # Logs gần đây
    recent_logs = AdminLog.objects.order_by('-timestamp')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'locked_users': locked_users,
        'total_posts': total_posts,
        'total_groups': total_groups,
        'locked_groups': locked_groups,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'active_groups': active_groups,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin, login_url='signin')
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_dashboard/manage_users.html', {'users': users})

@user_passes_test(is_admin, login_url='signin')
def manage_posts(request):
    # Lấy tham số tìm kiếm và sắp xếp từ URL
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'newest')

    # Bắt đầu với tất cả bài viết
    posts = Post.objects.all()

    # Áp dụng tìm kiếm nếu có
    if search_query:
        posts = posts.filter(
            Q(caption__icontains=search_query) |
            Q(user__icontains=search_query)
        )

    # Áp dụng sắp xếp
    if sort_by == 'oldest':
        posts = posts.order_by('created_at')
    elif sort_by == 'most_likes':
        posts = posts.order_by('-no_of_likes', '-created_at')
    else:  # newest
        posts = posts.order_by('-created_at')

    # Phân trang
    paginator = Paginator(posts, 10)  # 10 bài viết mỗi trang
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_dashboard/manage_posts.html', {'posts': page_obj})

@user_passes_test(is_admin, login_url='signin')
def manage_groups(request):
    groups = Group.objects.all().order_by('name')
    return render(request, 'admin_dashboard/manage_groups.html', {'groups': groups})

@user_passes_test(is_admin, login_url='signin')
def toggle_user_status(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.is_staff:
                messages.error(request, 'Không thể khóa tài khoản admin')
                return redirect('manage_users')
                
            user.is_active = not user.is_active
            user.save()
            
            action = 'Mở khóa' if user.is_active else 'Khóa'
            AdminLog.objects.create(
                admin=request.user,
                action=f'{action} tài khoản',
                target=user.username
            )
            
            messages.success(request, f'Đã {action.lower()} tài khoản {user.username}')
        except User.DoesNotExist:
            messages.error(request, 'Không tìm thấy người dùng')
    
    return redirect('manage_users')

@user_passes_test(is_admin, login_url='signin')
def toggle_group_status(request, group_id):
    if request.method == 'POST':
        try:
            group = Group.objects.get(id=group_id)
            group.is_locked = not group.is_locked
            group.save()
            
            action = 'Mở khóa' if not group.is_locked else 'Khóa'
            AdminLog.objects.create(
                admin=request.user,
                action=f'{action} nhóm',
                target=group.name
            )
            
            messages.success(request, f'Đã {action.lower()} nhóm {group.name}')
        except Group.DoesNotExist:
            messages.error(request, 'Không tìm thấy nhóm')
    
    return redirect('manage_groups')

@user_passes_test(is_admin, login_url='signin')
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            if user.is_staff:
                messages.error(request, 'Không thể xóa tài khoản admin')
                return redirect('manage_users')
                
            username = user.username
            user.delete()
            
            AdminLog.objects.create(
                admin=request.user,
                action='Xóa người dùng',
                target=username
            )
            
            messages.success(request, f'Đã xóa người dùng {username}')
        except User.DoesNotExist:
            messages.error(request, 'Không tìm thấy người dùng')
    
    return redirect('manage_users')

@user_passes_test(is_admin, login_url='signin')
def delete_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            post_user = post.user
            post.delete()
            
            AdminLog.objects.create(
                admin=request.user,
                action='Xóa bài viết',
                target=f'Bài viết của {post_user}'
            )
            
            messages.success(request, 'Đã xóa bài viết thành công')
        except Post.DoesNotExist:
            messages.error(request, 'Không tìm thấy bài viết')
    
    return redirect('manage_posts')

@user_passes_test(is_admin, login_url='signin')
def delete_group(request, group_id):
    if request.method == 'POST':
        try:
            group = Group.objects.get(id=group_id)
            group_name = group.name
            group.delete()
            
            AdminLog.objects.create(
                admin=request.user,
                action='Xóa nhóm',
                target=group_name
            )
            
            messages.success(request, f'Đã xóa nhóm {group_name}')
        except Group.DoesNotExist:
            messages.error(request, 'Không tìm thấy nhóm')
    
    return redirect('manage_groups') 