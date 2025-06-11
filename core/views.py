from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Group, Message, Product, ProductImage, Comment
from itertools import chain
import random
from django.db import models
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from datetime import datetime

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get follower and following counts
    user_followers = len(FollowersCount.objects.filter(user=request.user.username))
    user_following_count = len(FollowersCount.objects.filter(follower=request.user.username))

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # Thêm bài viết của người dùng hiện tại vào feed
    user_posts = Post.objects.filter(user=request.user.username)
    feed_list.extend(user_posts)

    # Sắp xếp lại theo thời gian tạo
    feed_list.sort(key=lambda x: x.created_at, reverse=True)

    # Get all unique usernames from posts
    post_usernames = set(post.user for post in feed_list)
    
    # Get profiles for all users who have posts
    profiles = {}
    for username in post_usernames:
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            profiles[username] = profile
        except (User.DoesNotExist, Profile.DoesNotExist):
            continue

    # User suggestions
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)
    
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list[:5]:  # Limit to 5 user suggestions
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    
    # Group suggestions
    all_groups = Group.objects.all().order_by('?')[:5]  # Get 5 random groups
    
    # Get user's joined groups
    user_joined_groups = Group.objects.filter(members__user=user_object).order_by('name')

    return render(request, 'MainPage.html', {
        'user_profile': user_profile, 
        'posts': feed_list, 
        'profiles': profiles,
        'suggestions_username_profile_list': suggestions_username_profile_list,
        'suggested_groups': all_groups,
        'user_followers': user_followers,
        'user_following': user_following_count,
        'joined_groups': user_joined_groups
    })

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.extend(profile_lists)

        # Tìm kiếm nhóm
        groups = Group.objects.filter(
            models.Q(name__icontains=username) | 
            models.Q(description__icontains=username)
        )
        
        # Lấy danh sách nhóm người dùng đã tham gia
        user_groups = Group.objects.filter(members__user=request.user)

        context = {
            'user_profile': user_profile,
            'username_profile_list': username_profile_list,
            'username': username,
            'groups': groups,
            'user_groups': user_groups,
        }

        return render(request, 'SearchPage.html', context)
    
    return render(request, 'SearchPage.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk).order_by('-created_at')  # Sort by creation time in descending order
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'ProfilePage.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    
    # Get following users (friends)
    following = FollowersCount.objects.filter(follower=request.user.username)
    following_users = []
    for follow in following:
        try:
            user = User.objects.get(username=follow.user)
            profile = Profile.objects.get(user=user)
            following_users.append({
                'user': user,
                'profile': profile
            })
        except (User.DoesNotExist, Profile.DoesNotExist):
            continue
            
    # Get groups user is a member of
    user_groups = Group.objects.filter(members__user=request.user)

    if request.method == 'POST':
        # Handle profile image upload
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get('image')
            
        # Handle cover photo upload
        if request.FILES.get('cover_photo') == None:
            cover_photo = user_profile.cover_photo
        else:
            cover_photo = request.FILES.get('cover_photo')
            
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.cover_photo = cover_photo
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        
        return redirect('settings')
    return render(request, 'SettingPage.html', {
        'user_profile': user_profile,
        'following_users': following_users,
        'user_groups': user_groups
    })

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'SignUpPage.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')

    else:
        return render(request, 'SignInPage.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def messages_page(request):
    # Get current user's profile
    user_profile = Profile.objects.get(user=request.user)
    
    # Get all conversations of the current user
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values('sender', 'receiver').distinct()
    
    # Get unique users that the current user has conversations with
    users_with_conversations = set()
    for conv in conversations:
        if conv['sender'] == request.user.id:
            users_with_conversations.add(conv['receiver'])
        else:
            users_with_conversations.add(conv['sender'])
    
    chat_users = User.objects.filter(id__in=users_with_conversations)
    
    # Get profiles for all chat users
    chat_users_with_profiles = []
    for user in chat_users:
        try:
            profile = Profile.objects.get(user=user)
            chat_users_with_profiles.append({
                'user': user,
                'profile': profile
            })
        except Profile.DoesNotExist:
            continue
    
    # If a specific chat is selected
    selected_user_id = request.GET.get('user_id')
    if selected_user_id:
        selected_user = User.objects.get(id=selected_user_id)
        selected_user_profile = Profile.objects.get(user=selected_user)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=selected_user)) |
            (Q(sender=selected_user) & Q(receiver=request.user))
        ).order_by('created_at')
        
        # Mark messages as read
        unread_messages = messages.filter(receiver=request.user, is_read=False)
        unread_messages.update(is_read=True)
    else:
        selected_user = None
        selected_user_profile = None
        messages = []
    
    context = {
        'user_profile': user_profile,
        'chat_users': chat_users_with_profiles,
        'selected_user': selected_user,
        'selected_user_profile': selected_user_profile,
        'messages': messages,
    }
    
    return render(request, 'MessagePage.html', context)

@login_required(login_url='signin')
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        
        if receiver_id and content:
            try:
                receiver = User.objects.get(id=receiver_id)
                message = Message.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    content=content
                )
                return JsonResponse({
                    'status': 'success',
                    'message': {
                        'content': message.content,
                        'created_at': message.created_at.strftime('%H:%M'),
                        'sender_username': message.sender.username,
                    }
                })
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required(login_url='signin')
def get_messages(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).order_by('created_at')
        
        messages_data = [{
            'content': msg.content,
            'sender_id': msg.sender.id,
            'created_at': msg.created_at.strftime('%H:%M'),
            'is_read': msg.is_read,
        } for msg in messages]
        
        return JsonResponse({'status': 'success', 'messages': messages_data})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})

@login_required(login_url='signin')
def edit_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            
            # Check if the user owns the post
            if post.user != request.user.username:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
            
            import json
            data = json.loads(request.body)
            caption = data.get('caption')
            
            if caption is not None:
                post.caption = caption
                post.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Caption is required'}, status=400)
                
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required(login_url='signin')
def delete_post(request, post_id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            
            # Check if the user owns the post
            if post.user != request.user.username:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
            
            # Delete the post
            post.delete()
            return JsonResponse({'status': 'success'})
                
        except Post.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = request.user
        
        # Check if current password is correct
        if not check_password(current_password, user.password):
            messages.error(request, 'Mật khẩu hiện tại không chính xác')
            return redirect('settings')
        
        # Check if new password is same as current password
        if check_password(new_password, user.password):
            messages.error(request, 'Mật khẩu mới không được trùng với mật khẩu hiện tại')
            return redirect('settings')
            
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp')
            return redirect('settings')
            
        # Check password length
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự')
            return redirect('settings')
            
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate user
        updated_user = auth.authenticate(username=user.username, password=new_password)
        auth.login(request, updated_user)
        
        messages.success(request, 'Mật khẩu đã được cập nhật thành công')
        return redirect('settings')
        
    return redirect('settings')

@login_required(login_url='signin')
def marketplace(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get filter parameters
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Base queryset
    products = Product.objects.filter(is_sold=False)

    # Apply filters
    if category and category != 'all':
        products = products.filter(category=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'user_profile': user_profile,
        'products': products,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'MarketPlace.html', context)

@login_required(login_url='signin')
def create_listing(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        location = request.POST.get('location')
        images = request.FILES.getlist('images')

        # Create product
        product = Product.objects.create(
            seller=request.user,
            title=title,
            description=description,
            price=price,
            category=category,
            location=location
        )

        # Create product images
        for image in images:
            ProductImage.objects.create(
                product=product,
                image=image
            )

        messages.success(request, 'Sản phẩm đã được đăng thành công!')
        return redirect('marketplace')

    return redirect('marketplace')

@login_required(login_url='signin')
def edit_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id, seller=request.user)
    except Product.DoesNotExist:
        messages.error(request, 'Không tìm thấy sản phẩm!')
        return redirect('marketplace')

    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.category = request.POST.get('category')
        product.location = request.POST.get('location')
        product.save()

        # Handle new images
        new_images = request.FILES.getlist('images')
        for image in new_images:
            ProductImage.objects.create(
                product=product,
                image=image
            )

        messages.success(request, 'Sản phẩm đã được cập nhật thành công!')
        return redirect('marketplace')

    return redirect('marketplace')

@login_required(login_url='signin')
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id, seller=request.user)
        product.delete()
        messages.success(request, 'Sản phẩm đã được xóa thành công!')
    except Product.DoesNotExist:
        messages.error(request, 'Không tìm thấy sản phẩm!')

    return redirect('marketplace')

@login_required(login_url='signin')
def product_detail(request, product_id):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    try:
        product = Product.objects.get(id=product_id)
        seller_profile = Profile.objects.get(user=product.seller)
        
        context = {
            'user_profile': user_profile,
            'product': product,
            'seller_profile': seller_profile,
        }
        return render(request, 'ProductDetail.html', context)
    except Product.DoesNotExist:
        return redirect('marketplace')

@login_required(login_url='signin')
def search_market(request):
    if request.method == 'POST':
        query = request.POST.get('search_query', '')
        user_profile = Profile.objects.get(user=request.user)

        products = Product.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(category__icontains=query) |
            models.Q(location__icontains=query),
            is_sold=False
        )

        context = {
            'user_profile': user_profile,
            'products': products,
            'search_query': query,
        }
        return render(request, 'MarketPlace.html', context)

    return redirect('marketplace')

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_text = request.POST.get('comment')
    
    if not comment_text:
        return JsonResponse({'status': 'error', 'message': 'Nội dung bình luận không được để trống'})

    comment = Comment.objects.create(
        post=post,
        user=request.user,
        text=comment_text
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Đã thêm bình luận',
        'comment': {
            'id': str(comment.id),
            'text': comment.text,
            'username': comment.user.username,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user_profile_img': comment.user.profile.profileimg.url if hasattr(comment.user, 'profile') and comment.user.profile.profileimg else None
        }
    })

@login_required(login_url='signin')
def post_detail(request, post_id):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    try:
        post = Post.objects.get(id=post_id)
        user_post_profile = Profile.objects.get(user=User.objects.get(username=post.user))
        
        # Get user followers count
        user_followers = len(FollowersCount.objects.filter(user=post.user))
        user_following = len(FollowersCount.objects.filter(follower=post.user))
        
        context = {
            'post': post,
            'user_profile': user_profile,
            'post_user_profile': user_post_profile,
            'user_followers': user_followers,
            'user_following': user_following,
        }
        return render(request, 'post_detail.html', context)
    except Post.DoesNotExist:
        return redirect('/')

@login_required(login_url='signin')
def share_to_profile(request, post_id):
    if request.method == 'POST':
        try:
            original_post = Post.objects.get(id=post_id)
            
            # Create a new shared post
            shared_post = Post(
                user=request.user.username,
                caption=f"Đã chia sẻ bài viết từ @{original_post.user}\n\n{original_post.caption}",
                is_shared=True,
                original_post=original_post,
                shared_at=datetime.now(),
                shared_by=request.user.username
            )
            
            # If original post has an image, copy it to the shared post
            if original_post.image:
                shared_post.image = original_post.image
            
            shared_post.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Bài viết đã được chia sẻ thành công'
            })
            
        except Post.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Không tìm thấy bài viết'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Phương thức không được hỗ trợ'
    }, status=405)