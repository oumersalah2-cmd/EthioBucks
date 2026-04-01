from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # This connects your tasks app to the main website
    path('tasks/', include('tasks.urls', namespace='tasks')),
    # Force all default auth login requests to use the custom tasks login page.
    path('accounts/login/', RedirectView.as_view(url='/tasks/login/', permanent=False)),
    path('accounts/', include('django.contrib.auth.urls')),
    # Redirect base URL to tasks application
    path('', RedirectView.as_view(url='/tasks/', permanent=False)),
]

# This block MUST be outside the square brackets [ ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



