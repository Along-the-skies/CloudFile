#================= Import ======================
from django.urls import path
from . import views

#================= URLs ======================
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
    path("signup/", views.signup, name="signup"),
    path('verify/<uidb64>/<token>/', views.verify, name='verify'),
  # new route
]
