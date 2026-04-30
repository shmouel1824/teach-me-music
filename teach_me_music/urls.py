from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('accounts.urls',   namespace='accounts')),
    path('',            login_required(TemplateView.as_view(template_name='loading.html')), name='loading'),
    path('play/',       include('exercises.urls',   namespace='exercises')),
    path('api/',        include('recognition.urls', namespace='recognition')),
    path('dashboard/',  include('dashboard.urls',   namespace='dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)