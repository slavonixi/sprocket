from django.urls import path, include
from . import logs

urlpatterns = [
    # path("admin/", admin.site.urls), # Se usi l'admin di Django

    # Namespace 'api' per la logica core/manutenzione (Report, Operation, HR)
    path("api/", include(("api.urls", "api"), namespace="api")),
    
    # Namespace 'inventory' per la logica logistica (Inventory, Masterdata)
    path("api/inventory/", include(("inventory.urls", "inventory"), namespace="inventory")),    
]           

# Una singola rotta di autenticazione globale è sufficiente
urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]