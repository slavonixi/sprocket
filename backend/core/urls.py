from django.urls import path, include
from . import logs
from django.contrib import admin
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


v1_patterns = (
    [
        path("administration/", include(("administration.urls", "administration"), namespace="administration")),
        path("inventory/", include(("inventory.urls", "inventory"), namespace="inventory")),
        path("report/", include(("report.urls", "report"), namespace="report")),
    ],
    "v1",
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(v1_patterns)),
    # Downloads or serves raw OpenAPI JSON/YAML schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI endpoint
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Optional: Redoc UI endpoint
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]