from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include


from api.views import get_list


def connect_react(request):
    return render(request, 'build/index.html')


urlpatterns = [
    path('cf/get_list/start=<int:start>end=<int:end>/', get_list, name='get_list'),
    path('', connect_react),
    path('login/', connect_react),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('external/', include('external.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
