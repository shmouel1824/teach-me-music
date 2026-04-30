import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .models import UserProfile


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("exercises:play")
    if request.method == "POST":
        data     = json.loads(request.body)
        username = data.get("username", "").strip()
        notes    = data.get("notes", [])
        if not username:
            return _err("Nom d'utilisateur requis.")
        if len(username) < 3:
            return _err("Nom d'utilisateur trop court (min 3 caractères).")
        if len(notes) != 5:
            return _err("Veuillez jouer exactement 5 notes.")
        if User.objects.filter(username=username).exists():
            return _err("Ce nom d'utilisateur est déjà pris.")
        user = User.objects.create_user(username=username, password=None)
        user.set_unusable_password()
        user.save()
        profile = UserProfile(user=user)
        profile.set_note_password(notes)
        profile.save()
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        return _ok({"redirect": "/play/"})
    return render(request, "accounts/register.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("exercises:play")
    if request.method == "POST":
        data     = json.loads(request.body)
        username = data.get("username", "").strip()
        notes    = data.get("notes", [])
        if not username or len(notes) != 5:
            return _err("Nom d'utilisateur et 5 notes requis.")
        try:
            user    = User.objects.get(username=username)
            profile = user.profile
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return _err("Nom d'utilisateur ou mélodie incorrects.")
        if not profile.check_note_password(notes):
            return _err("Nom d'utilisateur ou mélodie incorrects.")
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
        return _ok({"redirect": "/play/"})
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def _ok(data):
    return JsonResponse({"ok": True, **data})

def _err(msg):
    return JsonResponse({"ok": False, "error": msg}, status=400)
