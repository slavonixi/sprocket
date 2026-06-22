from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class InventoryError(APIException):
    """Classe base per errori di magazzino."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'inventory_error'
    
class InsufficientStockError(InventoryError):
    def __init__(self, requested_quantity, inventory_quantity, item_sku, unit_symbol):
        self.inventory_quantity = inventory_quantity
        self.requested_quantity = requested_quantity
        self.item_sku = item_sku
        self.unit_symbol = unit_symbol
        # Costruiamo un messaggio dinamico usando i parametri passati
        default_detail = _(f"il magazzino non disponde di {self.requested_quantity} {self.unit_symbol} per l'elemento {self.item_sku} ({self.inventory_quantity} {self.unit_symbol}).")
        super().__init__(default_detail)

class DecimalValueError(InventoryError):
    def __init__(self, unit_measure):
        self.unit_measure = unit_measure
        default_detail = _(f"L'unità di misura '{self.unit_measure}' non accetta valori decimali.")
        super().__init__(default_detail)        

class NegativeOrZeroError(InventoryError):
    def __init__(self):
        default_detail = _(f"Il valore deve esse > 0.")
        super().__init__(default_detail)          

class InsufficientStockForUpdate(InventoryError):
    def __init__(self):
        default_detail = _(f"La quantità aggiuntiva non è disponibile nel magazzino.")
        super().__init__(default_detail)          

class NoChangeDetectedInUpdate(InventoryError):
    def __init__(self, qta):
        default_detail = _(f"Inserisci una quantità diversa da {self.qta} durante la modifica.")
        super().__init__(default_detail)          

               