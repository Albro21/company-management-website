from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('users.urls')),
    path('accounts/', include('authentication.urls')),
    path('teams/', include('teams.urls', namespace='teams')),
    path('timetracker/', include('timetracker.urls', namespace='timetracker')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
