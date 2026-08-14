from inventory import exceptions
from django.db import transaction
from inventory.models import Inventory
from inventory.models import Inv_masterdata
from inventory.models import MeasureUnit
import logging
from rest_framework.exceptions import APIException # pyright: ignore

logger = logging.getLogger('django')

class InventoryServices:

    @staticmethod
    def debug(inv_id):
        return "InventoryServices tied"
    
#**********************************************************************************************
#**********************************************************************************************
#**********************************************************************************************

    #   
    #   Utility methods handle miscellaneous tasks by offering 
    #   ready-made logic for operations like constructing intricate
    #   function responses.
    #
    #
    #
    #
    # 

    #  | UTILS METHODS |
    #  | UTILS METHODS |
    #  | UTILS METHODS |
    #  | UTILS METHODS |
    #  | UTILS METHODS |
    #  | UTILS METHODS |

    @staticmethod
    def create_return_response(*, status="success", operation="not specified", withdrawed_qty, item):
        """create a ready-to-use response for any inventory operation:

        PROVIDED:
            withdrawed_qty
            final_qty
            measure_unit
        """
        measure_unit = item.get_unit_measure()
        result = {
            "status": status,
            "operation": operation,
            "data": {
                "withdrawed_qty": float(withdrawed_qty), # Quantità movimentata
                "final_qty": float(item.quantity),           # Giacenza residua [3]
                "measure_unit": {
                    "symbol": measure_unit.symbol,       # Es: "kg" o "pz" [2]
                    "name": measure_unit.name            # Es: "Kilogrammo" [2]
                }
            }            
        }
        return result

    @staticmethod
    def get_delta(old_qty, new_qty):
        delta = old_qty - new_qty
        return delta
    
    @staticmethod
    def compare_qty(qty1, qty2):
        if qty1 == qty2:
            raise exceptions.NoChangeDetectedInUpdate(qty1)
        return True

    @staticmethod
    def is_not_zero(qty):
        """check if the value is zero, raise
           a NegativeOrZeroError exception.

           In some operations, negative values are forbidden.
           Zero values are forbidden in every operation.
        
        """
        if qty <= 0:
            raise exceptions.NegativeOrZeroError(qty)

    @staticmethod
    def check_decimal(inventory_item, qty=False):
        """ Ensure measures limits are followed.
            e.g. 10.4 pz is an irregular value
                 (pieces cannot be decimal)
                 10.4 kg is a regular value
        """
        #value = false -> check if quantity is valid in insertion
        if not qty:
            qty = inventory_item.quantity
        #value != false -> check if a draft quantity to add or remove is valid
        
        if qty % 1: #check if the number is integer or not
            if not inventory_item.is_allowed_decimal_value():
                raise exceptions.DecimalValueError(inventory_item, qty)
        
        return True

    @staticmethod    
    def is_sufficient(inventory_item, qta_to_remove):
        """Check if there are enough items to withdraw.
        
           !!! Always take a positive qta_to_remove !!!
        """
        if inventory_item.quantity < qta_to_remove:
            raise exceptions.InsufficientStockError(
                qta_to_remove, 
                inventory_item,
            )  
        return True
    
#**********************************************************************************************
#**********************************************************************************************
#**********************************************************************************************




    #   Validation methods perform checks to every item that has
    #   to enter or exit the inventory. 
    # 
    #   They don't apply any changes at the models.
    #
    #   Trigger exceptions when irregularity occours.
    #
    # 

    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |



    @staticmethod
    def validate_stock_operation(inventory_item, movement_qty):
        """
            Check if a movement create operation is valid and match inventory's rules
        """
        try:    
            #movement_qty must be != 0
            InventoryServices.is_not_zero(movement_qty)      
            #check if decimal values are accepted for this item
            InventoryServices.check_decimal(inventory_item, movement_qty)
            if movement_qty < 0: #if the movement is an outbound operation check if the stock is sufficient
                InventoryServices.is_sufficient(inventory_item, movement_qty)
        except exceptions.InventoryError as e:
            raise e
        return True

    def validate_item(inventory_item):
        return True

#**********************************************************************************************
#**********************************************************************************************
#**********************************************************************************************
    #
    #  Service methods apply the final changes to inventory model. 
    #  In most of cases, they are called by the orchestrator class:
    #   AppServices
    #
    #  | SERVICE METHODS |
    #  | SERVICE METHODS |
    #  | SERVICE METHODS |
    #  | SERVICE METHODS |
    #  | SERVICE METHODS |
    #  | SERVICE METHODS |

    @staticmethod
    def create_stock(inventory_item):
        inventory_item.save()
        return inventory_item

    @staticmethod
    def add_value_to_stock(inventory_id, qty): 
        """
        add the qty value of an inventory element. It performs a stock
        availability check to avoid 'critical race' issues.
            
        """
        with transaction.atomic():
            inventory_item = Inventory.objects.select_for_update().get(id=inventory_id)
            if qty < 0: #if true -> withdraw | if false -> restore
                try:
                    InventoryServices.is_sufficient(inventory_item, -qty)
                except exceptions.InsufficientStockError as e:
                    raise e
            inventory_item.quantity += qty 
            inventory_item.save()
            result = InventoryServices.create_return_response(
                operation = "InventoryServices.add_value_to_stock",
                withdrawed_qty = qty,
                item = inventory_item,
            )
            return result

    def update_stock_value(inventory_id, old_qty, new_qty):
        delta = InventoryServices.get_delta(old_qty, new_qty)
        result = InventoryServices.add_value_to_stock(inventory_id, delta)
        return result

    def delete_stock(inventory_item):
        inventory_item.delete()
        return True