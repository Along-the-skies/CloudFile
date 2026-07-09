from django.contrib import admin
from .models   import SharedFile
from django.urls import path, include

admin.site.register(SharedFile)
# Register your models here.
