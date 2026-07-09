#================= Imports ======================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from .models import SharedFile, DownloadLog
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

#================= Helper Functions ======================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#================= Views ======================
def home(request):
    return render(request, 'CloudFile/home.html')

@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        shared = SharedFile(file=uploaded_file, owner=request.user)
        shared.save()
        return render(request, 'CloudFile/success.html', {'file': shared})
    return render(request, 'CloudFile/upload.html')

def download_file(request, file_id):
    shared = get_object_or_404(SharedFile, id=file_id)
    ip = get_client_ip(request)
    DownloadLog.objects.create(file=shared, ip_address=ip)
    return FileResponse(shared.file.open(), as_attachment=True)

#================= Signup ======================
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        # prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            return render(request, "CloudFile/signup.html", {"error": "Username already exists"})
        if User.objects.filter(email=email).exists():
            return render(request, "CloudFile/signup.html", {"error": "Email already registered"})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # deactivate until email verified
        user.save()

        # generate token + uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # verification link
        link = f"http://127.0.0.1:8000/verify/{uid}/{token}/"

        # send email
        send_mail(
            "Verify your CloudFile account",
            f"Click here to verify your account: {link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )

        return render(request, "CloudFile/verify_sent.html")
    return render(request, "CloudFile/signup.html")

#================= Verification ======================
def verify(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, "CloudFile/verify_success.html")
    else:
        return render(request, "CloudFile/verify_failed.html")
