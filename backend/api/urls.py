from django.urls import path, include
from rest_framework.routers import DefaultRouter #pyright: ignore
from . import views
# Create a router and register our Viewets with it.
app_name = 'api'
router = DefaultRouter()
router.register(r"/hr_records", views.HR_recordsViewSet, basename="hr_records")
router.register(r"/report", views.ReportViewSet, basename="report")
router.register(r"/customer_records", views.Customer_recordsViewSet, basename="customer_records")
router.register(r"/operation", views.OperationViewSet, basename="operation")
router.register(r"/machinery_records", views.Machinery_recordsViewSet, basename="machinery_records")
router.register(r"/usedmaterials", views.UsedMaterialsViewSet, basename="usedmaterials")
router.register(r"/logs", views.LogsViewSet, basename="logs")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]   


