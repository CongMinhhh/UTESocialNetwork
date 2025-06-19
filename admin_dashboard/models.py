from django.db import models
from django.contrib.auth.models import User

class AdminLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.timestamp}" 