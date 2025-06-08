from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Group, GroupMember, GroupPost, GroupComment, GroupJoinRequest, Message

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(GroupPost)
admin.site.register(GroupComment)
admin.site.register(GroupJoinRequest)
admin.site.register(Message)