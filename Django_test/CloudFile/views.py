#================= Imports ======================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from .models import SharedFile, DownloadLog
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

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
    files = None
    if request.user.is_authenticated:
        files = SharedFile.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'CloudFile/home.html', {'files': files})

from django.urls import reverse

@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return render(request, 'CloudFile/upload.html', {
                'error': 'No file selected. Please choose a file to upload.'
            })
        shared = SharedFile(file=uploaded_file, owner=request.user)
        shared.save()
        shared.set_expiry(days=3)

        # Build absolute link with domain
        download_link = request.build_absolute_uri(
            reverse('download', kwargs={'file_id': shared.id})
        )

        return render(request, 'CloudFile/success.html', {
            'file': shared,
            'download_link': download_link
        })
    return render(request, 'CloudFile/upload.html')


def download_page(request, file_id):
    shared = get_object_or_404(SharedFile, id=file_id)
    if shared.is_expired():
        return render(request, "CloudFile/expired.html", {"file": shared})
    return render(request, "CloudFile/download.html", {"file": shared})



def download_file(request, file_id):
    shared = get_object_or_404(SharedFile, id=file_id)
    if shared.is_expired():
        return render(request, "CloudFile/expired.html", {"file": shared})
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

        # verification link for current host
        link = request.build_absolute_uri(reverse("verify", kwargs={"uidb64": uid, "token": token}))

        # send email
        try:
            send_mail(
                "Verify your CloudFile account",
                f"Click here to verify your account: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
        except Exception:
            return render(request, "CloudFile/signup.html", {"error": "Unable to send verification email. Please try again later."})

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
