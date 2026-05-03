from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.shortcuts import render

def loading_view(request):
    get_token(request)  # forces CSRF cookie to be set
    return render(request, 'loading.html')

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('accounts.urls',   namespace='accounts')),
    path('',            loading_view, name='loading'),
    path('play/',       include('exercises.urls',   namespace='exercises')),
    path('api/',        include('recognition.urls', namespace='recognition')),
    path('dashboard/',  include('dashboard.urls',   namespace='dashboard')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)