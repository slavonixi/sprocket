from django.urls import path, include
from . import logs
from django.contrib import admin



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
]