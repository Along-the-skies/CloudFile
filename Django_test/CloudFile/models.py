from django.db import models
from django.contrib.auth.models import User
import uuid

class SharedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='shared_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # who uploaded

    def __str__(self):
        return str(self.file.name)


class DownloadLog(models.Model):
    file = models.ForeignKey(SharedFile, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    downloaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file} downloaded from {self.ip_address}"
