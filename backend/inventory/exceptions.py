from rest_framework.exceptions import APIException #pyright: ignore
from rest_framework import status #pyright: ignore
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
    """Parent class for the inventory/stock errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Exception.Inventory'

class SerializerError(APIException):
    """Parent class for the serializers-oriented errors"""
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = 'Exception.Serializer'

############################
### Inventory Exceptions ###
############################

    
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

class ZeroError(InventoryError):
    def __init__(self, op = 'stock_adjust'):
        default_detail = 'Exception.Inventory.ZeroError'
        result = buildMessage(
            operation = op,
            code = default_detail,
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

class MovementQtyIsZeroOrNegativeError(InventoryError):
    def __init__(self, op="inventory_movement"):
        default_detail = InventoryError.default_code + ".MovementQtyIsZeroOrNegativeError"
        result = buildMessage(
            operation=op,
            code = default_detail,
        )
        super().__init__(result)

class IllegalOperationValue(InventoryError):
    def __init__(self, illegal_value, op="movement_create"):
        default_detail = InventoryError.default_code + ".IllegalOperationValue"
        data = {
            'illegal_value': illegal_value
        }
        result = buildMessage(
            operation=op,
            code = default_detail,
            **data,
        )
        super().__init__(result)


###########################
## Serializer Exceptions ##
###########################

class UpdateOrDeleteIsForbidden(SerializerError):
    def __init__(self, op="update_or_delete_movement"):
        default_detail = self.default_detail+".UpdateOrDeleteIsForbidden"
        result = buildMessage(
            operation=op,
            code = default_detail,
        )
        super().__init__(result)