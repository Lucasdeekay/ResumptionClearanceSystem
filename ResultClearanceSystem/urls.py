from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from ResultClearanceSystem import settings

schema_view = get_schema_view(
   openapi.Info(
      title="Automated Result Clearance System",
      default_version='v1',
      description="API description",
      terms_of_service="https://yourwebsite.com/terms/",
      contact=openapi.Contact(email="contact@yourwebsite.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('MySite.urls')),  # Replace with your app URL path
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Conditional inclusion of media and static URL patterns (based on DEBUG)
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) if settings.DEBUG else [],
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else [],
]