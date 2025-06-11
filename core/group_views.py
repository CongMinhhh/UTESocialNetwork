from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, GroupMember, GroupPost, GroupJoinRequest
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Profile

@login_required
def create_group(request):
    user_profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_private = request.POST.get('is_private', False)
        avatar = request.FILES.get('avatar')
        cover_photo = request.FILES.get('cover_photo')

        if Group.objects.filter(name=name).exists():
            messages.error(request, 'Tên nhóm đã tồn tại')
            return redirect('create_group')

        group = Group.objects.create(
            name=name,
            description=description,
            admin=request.user,
            is_private=is_private == 'true'
        )

        # Handle avatar upload
        if avatar:
            group.profile_image = avatar
            
        # Handle cover photo upload
        if cover_photo:
            group.cover_photo = cover_photo
            
        group.save()

        GroupMember.objects.create(
            group=group,
            user=request.user
        )

        messages.success(request, 'Tạo nhóm thành công!')
        return redirect('group_detail', group_id=group.id)

    return render(request, 'create_group.html', {'user_profile': user_profile})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Get user profile
    user_profile = Profile.objects.get(user=request.user)
    
    # Check if user is a member
    is_member = GroupMember.objects.filter(group=group, user=request.user).exists()
    
    # Check if user is admin
    is_admin = group.admin == request.user
    
    # Get group posts with pagination
    posts = group.posts.all().order_by('-created_at')
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get suggested groups
    suggested_groups = Group.objects.exclude(id=group_id).order_by('?')[:5]

    context = {
        'group': group,
        'is_member': is_member,
        'is_admin': is_admin,
        'posts': page_obj,
        'suggested_groups': suggested_groups,
        'user_profile': user_profile
    }
    return render(request, 'GroupPage.html', context)

@login_required
def group_settings(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.admin != request.user:
        messages.error(request, 'Bạn không có quyền quản lý nhóm này')
        return redirect('group_detail', group_id=group.id)
    
    pending_requests = GroupJoinRequest.objects.filter(
        group=group,
        status='pending'
    ).order_by('-created_at')

    user_profile = Profile.objects.get(user=request.user)

    context = {
        'group': group,
        'pending_requests': pending_requests,
        'user_profile': user_profile
    }
    return render(request, 'SettingGroupPage.html', context)

@login_required
@require_POST
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.admin != request.user:
        messages.error(request, 'Bạn không có quyền chỉnh sửa nhóm này')
        return redirect('group_detail', group_id=group.id)

    # Handle profile image upload
    if request.FILES.get('profile_image'):
        group.profile_image = request.FILES.get('profile_image')
            
    # Handle cover photo upload
    if request.FILES.get('cover_photo'):
        group.cover_photo = request.FILES.get('cover_photo')

    group.name = request.POST.get('name')
    group.description = request.POST.get('description')
    group.is_private = request.POST.get('is_private') == 'true'
    group.save()

    messages.success(request, 'Cập nhật thông tin nhóm thành công')
    return redirect('group_settings', group_id=group.id)

@login_required
@require_POST
def remove_member(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    if group.admin != request.user:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền thực hiện'})

    member = get_object_or_404(User, id=user_id)
    GroupMember.objects.filter(group=group, user=member).delete()
    return JsonResponse({'status': 'success', 'message': 'Đã xóa thành viên'})

@login_required
@require_POST
def toggle_admin(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    if group.admin != request.user:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền thực hiện'})

    member = get_object_or_404(User, id=user_id)
    group_member = get_object_or_404(GroupMember, group=group, user=member)
    group_member.is_admin = not group_member.is_admin
    group_member.save()

    return JsonResponse({
        'status': 'success',
        'message': f'Đã {"cấp" if group_member.is_admin else "gỡ"} quyền quản trị'
    })

@login_required
@require_POST
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if GroupMember.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'Bạn đã là thành viên của nhóm'})

    if group.is_private:
        join_request, created = GroupJoinRequest.objects.get_or_create(
            group=group,
            user=request.user,
            defaults={'status': 'pending'}
        )
        if created:
            return JsonResponse({'status': 'success', 'message': 'Đã gửi yêu cầu tham gia nhóm'})
        return JsonResponse({'status': 'error', 'message': 'Yêu cầu tham gia đang chờ xử lý'})
    else:
        GroupMember.objects.create(group=group, user=request.user)
        return JsonResponse({'status': 'success', 'message': 'Đã tham gia nhóm thành công'})

@login_required
@require_POST
def create_group_post(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'Bạn không phải là thành viên của nhóm'})

    content = request.POST.get('content')
    image = request.FILES.get('image')

    post = GroupPost.objects.create(
        group=group,
        user=request.user,
        content=content,
        image=image if image else None
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Đăng bài thành công',
        'post_id': str(post.id)
    })

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': post.likes.count()
    })

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    comment_text = request.POST.get('comment')
    
    if not comment_text:
        return JsonResponse({'status': 'error', 'message': 'Nội dung bình luận không được để trống'})

    comment = post.comments.create(
        user=request.user,
        text=comment_text
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Đã thêm bình luận',
        'comment_id': comment.id
    })

@login_required
def manage_group_requests(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.admin != request.user:
        messages.error(request, 'Bạn không có quyền quản lý nhóm này')
        return redirect('group_detail', group_id=group.id)

    pending_requests = GroupJoinRequest.objects.filter(
        group=group,
        status='pending'
    ).order_by('-created_at')

    context = {
        'group': group,
        'pending_requests': pending_requests
    }
    return render(request, 'manage_group_requests.html', context)

@login_required
@require_POST
def handle_join_request(request, request_id):
    join_request = get_object_or_404(GroupJoinRequest, id=request_id)
    if join_request.group.admin != request.user:
        return JsonResponse({'status': 'error', 'message': 'Không có quyền thực hiện'})

    action = request.POST.get('action')
    if action == 'accept':
        join_request.status = 'accepted'
        join_request.save()
        GroupMember.objects.create(
            group=join_request.group,
            user=join_request.user
        )
        message = 'Đã chấp nhận yêu cầu tham gia'
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.save()
        message = 'Đã từ chối yêu cầu tham gia'
    else:
        return JsonResponse({'status': 'error', 'message': 'Hành động không hợp lệ'})

    return JsonResponse({'status': 'success', 'message': message}) 

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    group = post.group

    # Check if user has permission to delete the post
    if post.user != request.user and group.admin != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'Bạn không có quyền xóa bài viết này'
        })

    post.delete()
    return JsonResponse({
        'status': 'success',
        'message': 'Đã xóa bài viết'
    }) 