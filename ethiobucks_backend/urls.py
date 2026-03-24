from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This connects your tasks app to the main website
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# This block MUST be outside the square brackets [ ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



