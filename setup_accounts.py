"""
setup_accounts.py
-----------------
Place ce script dans le dossier RACINE du projet (à côté de manage.py)
puis lance : python setup_accounts.py
"""
import os
import shutil
import subprocess
import sys

BASE = os.getcwd()  # Must be run from the project folder (where manage.py is)
if not os.path.exists(os.path.join(BASE, 'manage.py')):
    print("\n❌ Erreur: Lance ce script depuis le dossier qui contient manage.py")
    print("   Exemple: cd /chemin/vers/teach_me_music && python setup_accounts.py")
    sys.exit(1)

# Django config folder = subdirectory with same name as project
PROJECT_NAME = os.path.basename(BASE)
DJANGO_DIR   = os.path.join(BASE, PROJECT_NAME)

def make(path):
    os.makedirs(path, exist_ok=True)
    print(f"  📁 {path}")

def touch(path):
    if not os.path.exists(path):
        open(path, 'w').close()
    print(f"  📄 {path}")

def write(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅ {path}")

print("\n🎵 Teach Me Music — Installation du système de login\n")

# ── 1. Créer les dossiers ─────────────────────────────────────
print("1️⃣  Création des dossiers...")
make(os.path.join(BASE, 'accounts'))
make(os.path.join(BASE, 'accounts', 'migrations'))
make(os.path.join(BASE, 'templates', 'accounts'))
touch(os.path.join(BASE, 'accounts', '__init__.py'))
touch(os.path.join(BASE, 'accounts', 'migrations', '__init__.py'))

# ── 2. accounts/models.py ─────────────────────────────────────
print("\n2️⃣  Création des fichiers Python...")
write(os.path.join(BASE, 'accounts', 'models.py'), '''\
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password


class UserProfile(models.Model):
    """Extends Django User with a musical note password."""
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    note_password = models.CharField(max_length=255)
    created_at    = models.DateTimeField(auto_now_add=True)

    def set_note_password(self, note_sequence):
        raw = "-".join(note_sequence)
        self.note_password = make_password(raw)

    def check_note_password(self, note_sequence):
        raw = "-".join(note_sequence)
        return check_password(raw, self.note_password)

    def __str__(self):
        return f"Profile({self.user.username})"
''')

# ── 3. accounts/views.py ──────────────────────────────────────
write(os.path.join(BASE, 'accounts', 'views.py'), '''\
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
            return _err("Nom d\'utilisateur requis.")
        if len(username) < 3:
            return _err("Nom d\'utilisateur trop court (min 3 caractères).")
        if len(notes) != 5:
            return _err("Veuillez jouer exactement 5 notes.")
        if User.objects.filter(username=username).exists():
            return _err("Ce nom d\'utilisateur est déjà pris.")
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
            return _err("Nom d\'utilisateur et 5 notes requis.")
        try:
            user    = User.objects.get(username=username)
            profile = user.profile
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return _err("Nom d\'utilisateur ou mélodie incorrects.")
        if not profile.check_note_password(notes):
            return _err("Nom d\'utilisateur ou mélodie incorrects.")
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
''')

# ── 4. accounts/urls.py ───────────────────────────────────────
write(os.path.join(BASE, 'accounts', 'urls.py'), '''\
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/",    views.login_view,    name="login"),
    path("logout/",   views.logout_view,   name="logout"),
]
''')

# ── 5. Nettoyer les anciennes migrations si elles existent ───
mig_dir = os.path.join(BASE, 'accounts', 'migrations')
for f in os.listdir(mig_dir):
    if f.startswith('0') and f.endswith('.py'):
        os.remove(os.path.join(mig_dir, f))
        print(f"  🗑️  Ancienne migration supprimée: {f}")
print("  ✅ migrations/ prêt (sera généré par Django)")

# ── 6. Patch settings.py ──────────────────────────────────────
print("\n3️⃣  Mise à jour de settings.py...")
settings_path = os.path.join(DJANGO_DIR, 'settings.py')
with open(settings_path, 'r', encoding='utf-8') as f:
    s = f.read()

if "'accounts'" not in s:
    s = s.replace(
        "    'dashboard',\n]",
        "    'dashboard',\n    'accounts',\n]\n\n"
        "# Auth redirects\n"
        "LOGIN_URL           = '/accounts/login/'\n"
        "LOGIN_REDIRECT_URL  = '/play/'\n"
        "LOGOUT_REDIRECT_URL = '/accounts/login/'\n"
    )
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(s)
    print("  ✅ accounts ajouté à INSTALLED_APPS + redirections auth")
else:
    print("  ⏭️  settings.py déjà à jour")

# ── 7. Réécrire urls.py complètement ────────────────────────
print("\n4️⃣  Mise à jour de teach_me_music/urls.py...")
urls_path = os.path.join(DJANGO_DIR, 'urls.py')
urls_content = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('accounts.urls',   namespace='accounts')),
    path('',            TemplateView.as_view(template_name='loading.html'), name='loading'),
    path('play/',       include('exercises.urls',   namespace='exercises')),
    path('api/',        include('recognition.urls', namespace='recognition')),
    path('dashboard/',  include('dashboard.urls',   namespace='dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
with open(urls_path, 'w', encoding='utf-8') as f:
    f.write(urls_content)
print("  ✅ urls.py réécrit correctement")

# ── 8. Patch exercises/views.py ───────────────────────────────
print("\n5️⃣  Ajout de @login_required aux vues...")
for vpath, fname, viewname in [
    (os.path.join(BASE, 'exercises', 'views.py'), 'exercises/views.py', 'def play('),
    (os.path.join(BASE, 'dashboard', 'views.py'), 'dashboard/views.py', 'def dashboard('),
]:
    with open(vpath, 'r', encoding='utf-8') as f:
        v = f.read()
    changed = False
    if 'from django.contrib.auth.decorators import login_required' not in v:
        v = v.replace('from django.shortcuts import render',
                      'from django.shortcuts import render\nfrom django.contrib.auth.decorators import login_required', 1)
        changed = True
    if '@login_required\n' + viewname not in v and viewname in v:
        v = v.replace(viewname, '@login_required\n' + viewname, 1)
        changed = True
    if changed:
        with open(vpath, 'w', encoding='utf-8') as f:
            f.write(v)
        print(f"  ✅ @login_required ajouté à {fname}")
    else:
        print(f"  ⏭️  {fname} déjà à jour")

# ── 9. Run makemigrations + migrate ──────────────────────────
print("\n6️⃣  Migration de la base de données...")
r1 = subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'accounts'],
                    capture_output=True, text=True, cwd=BASE)
if r1.returncode == 0:
    print("  ✅ makemigrations réussi !")
else:
    print("  ❌ Erreur makemigrations:")
    print(r1.stderr)
    sys.exit(1)

r2 = subprocess.run([sys.executable, 'manage.py', 'migrate'],
                    capture_output=True, text=True, cwd=BASE)
if r2.returncode == 0:
    print("  ✅ migrate réussi !")
else:
    print("  ❌ Erreur migrate:")
    print(r2.stderr)

print("\n" + "="*50)
print("✅ Installation terminée !")
print("="*50)
print("\nMaintenant :")
print("  1. Copie register.html → templates/accounts/register.html")
print("  2. Copie login.html    → templates/accounts/login.html")
print("  3. Redémarre Django : python manage.py runserver")
print("\nURL d'inscription : http://127.0.0.1:8000/accounts/register/")
print("URL de connexion  : http://127.0.0.1:8000/accounts/login/\n")