from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', include('adminpage.urls')),
    path('', include('pagesiswa.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
