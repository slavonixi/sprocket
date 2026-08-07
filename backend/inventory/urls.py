from django.urls import path, include
from rest_framework.routers import DefaultRouter #pyright: ignore
from . import views
# Create a router and register our Viewets with it.
app_name = 'inventory'
router = DefaultRouter()
router.register(r"/inventory", views.InventoryViewSet, basename="inventory")
router.register(r"/inv_masterdata", views.MasterdataViewSet, basename="inv_masterdata")
router.register(r"/measure_unit", views.MeasureUnitViewSet, basename="measure_unit")
router.register(r"/movement", views.MovementViewSet, basename="movement")

# The API URLs are now determined automatically by the router.


urlpatterns = [
    path("", include(router.urls)),
]


