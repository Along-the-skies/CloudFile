#================= Import ======================
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

#================= URLs ======================
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('download/<uuid:file_id>/', views.download_file, name='download'),
    path("signup/", views.signup, name="signup"),
    path('verify/<uidb64>/<token>/', views.verify, name='verify'),
    path('download_page/<uuid:file_id>/', views.download_page, name='download_page'),
    path('logout/',auth_views.LogoutView.as_view(next_page='',http_method_names=["get", "post"]), name='logout',)
  # new route
]
