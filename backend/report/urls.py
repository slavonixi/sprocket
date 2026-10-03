from django.urls import path, include
from rest_framework.routers import DefaultRouter #pyright: ignore
from report import views
# Create a router and register our Viewets with it.
app_name = 'report'
router = DefaultRouter()
router.register(r"report", views.ReportViewSet, basename="report")
router.register(r"operation", views.OperationViewSet, basename="operation")
router.register(r"used_material", views.UsedMaterialsViewSet, basename="used_materials")

# The API URLs are now determined automatically by the router.


urlpatterns = [
    path("", include(router.urls)),
]


