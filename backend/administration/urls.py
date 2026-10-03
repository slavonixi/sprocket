from django.urls import path, include
from rest_framework.routers import DefaultRouter #pyright: ignore
from . import views
# Create a router and register our Viewets with it.
app_name = 'administration'
router = DefaultRouter()
router.register(r"hr_records", views.HR_recordsViewSet, basename="hr_records")
router.register(r"customer_records", views.Customer_recordsViewSet, basename="customer_records")
router.register(r"machinery_records", views.Machinery_recordsViewSet, basename="machinery_records")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]   


