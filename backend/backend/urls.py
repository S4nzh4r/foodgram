from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api.views import redirect_from_short_link

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('r/<str:short_code>/',
         redirect_from_short_link,
         name='short_link_redirect')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
