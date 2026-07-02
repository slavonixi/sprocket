from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

def buildMessage(*, status="failed", operation="not specified", code, **kwargs):

    data = {}
    for key, value in kwargs.items():
        data[key] = value
    message = {
        "status": status,
        "operation": operation,
        "code": code,
        "data": data,
    }
    return message

class InventoryError(APIException):
    """Classe base per errori di magazzino."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'inventory_error'
    
class InsufficientStockError(InventoryError):
    def __init__(self, requested_quantity, inventory_item, op='withdraw'):
        data = {
            'requested_quantity' : requested_quantity,
            'inventory_quantity' : inventory_item.quantity,
            'item_sku' : inventory_item.get_sku(),
            'unit_symbol' : inventory_item.get_unit_measure().symbol,
        }
        default_detail = 'Exception.Inventory.InsufficientStockError'
        result = buildMessage(
            status='failure',
            operation=op,
            code=default_detail,
            **data,
        )
        super().__init__(result)

class DecimalValueError(InventoryError):
    def __init__(self, inventory_item, qty, op = 'stock_adjust'):
        data = {
            'SKU' : inventory_item.get_sku(),
            'inserted_quantity' : qty,
            'unit_measure' : inventory_item.get_unit_measure().symbol
        }
        default_detail = 'Exception.Inventory.DecimalValueError'
        result = buildMessage(
            status='failure',
            operation=op,
            code = default_detail,
            **data,
        )
        super().__init__(result)        

class NegativeOrZeroError(InventoryError):
    def __init__(self, qta ,op = 'stock_adjust'):
        data = {
            'inserted_quantity' : qta
        }
        default_detail = 'Exception.Inventory.NegativeOrZeroError'
        result = buildMessage(
            operation = op,
            code = default_detail,
            **data,
        )
        super().__init__(result)          

class NoChangeDetectedInUpdate(InventoryError):
    def __init__(self, qta):
        data = {
            'invalid_qty' : qta,
        }
        default_detail = 'Exception.Inventory.NoChangeDetectedInUpdate'
        result = buildMessage(
            operation='withdraw_update',
            code=default_detail,
            **data,
        )
        super().__init__(result)          

               