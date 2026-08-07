from django.urls import path, include
from . import logs

urlpatterns = [
    path("api", include("api.urls")),
    path("api/inventory", include("inventory.urls")),    
]           

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]   
urlpatterns += [
    path("inventory-auth/", include("rest_framework.urls")),
]   
