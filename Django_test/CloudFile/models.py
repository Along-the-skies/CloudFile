from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta

class SharedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='shared_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # expiry timestamp
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def set_expiry(self, days=3):
        """Default expiry: 1 day after upload"""
        self.expires_at = timezone.now() + timedelta(days=days)


    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at


class DownloadLog(models.Model):
    file = models.ForeignKey(SharedFile, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file} downloaded from {self.ip_address}"
