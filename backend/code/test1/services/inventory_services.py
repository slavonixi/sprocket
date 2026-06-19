from test1 import exceptions
from django.db import transaction
from test1.models import Inventory
from test1.models import Inv_masterdata
from test1.models import MeasureUnit
import logging
logger = logging.getLogger('django')

class InventoryServices:

    @staticmethod
    def debug(inv_id):
        return "InventoryServices tied"
    
#**********************************************************************************************
#**********************************************************************************************
#**********************************************************************************************

    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |
    #  | VALIDATION METHODS |


    @staticmethod
    def validate_item(inventory_item):
        InventoryServices.check_zero_or_negative(inventory_item.quantity)
        InventoryServices.check_decimal(inventory_item)

    @staticmethod
    def check_zero_or_negative(qta):
        if qta <= 0:
            raise exceptions.NegativeOrZeroError()


    @staticmethod
    def check_decimal(inventory_item, qty=False):
        #value = false -> check if quantity is valid in insertion
        if not qty:
            qty = inventory_item.quantity
        #value != false -> check if a draft quantity to add or remove is valid
        
        if qty % 1: #check if the number is integer or not
            if not inventory_item.is_allowed_decimal_value():
                raise exceptions.DecimalValueError(inventory_item.get_unit_measure())
        
        return True
    @staticmethod    
    def is_sufficient(inventory_item, qta_to_remove):
        if inventory_item.quantity < qta_to_remove:
            raise exceptions.InsufficientStockError(
                qta_to_remove, 
                inventory_item.quantity, 
                inventory_item.get_sku(),
                inventory_item.get_unit_measure(),
            )  
        return True
    
    @staticmethod
    def validate_stock_value(inventory_item, qta):

        InventoryServices.check_zero_or_negative(qta) 
        #check if decimal values are accepted for this item
        InventoryServices.check_decimal(inventory_item, qta)
        return True

    def validate_stock_reduction(inventory_item, qta_to_remove):
        InventoryServices.validate_stock_value(inventory_item, qta_to_remove)
        InventoryServices.is_sufficient(inventory_item, qta_to_remove)
        

    def validate_stock_update(inventory_item, old_qta, new_qta):
        if old_qta == new_qta:
            raise exceptions.NoChangeDetectedInUpdate(new_qta)
        
        delta = old_qta-new_qta
        if delta < 0:
            InventoryServices.validate_stock_reduction(inventory_item, -delta)
        else:
            InventoryServices.validate_stock_value(inventory_item, delta)
        return True
#**********************************************************************************************
#**********************************************************************************************
#**********************************************************************************************
    #   end of validation methods
    #
    #  | ORCHESTRATOR METHODS |
    #  | ORCHESTRATOR METHODS |
    #  | ORCHESTRATOR METHODS |
    #  | ORCHESTRATOR METHODS |
    #  | ORCHESTRATOR METHODS |
    #  | ORCHESTRATOR METHODS |

    
    @staticmethod
    def apply_to_stock(inventory_id, qta): 
        """
        Withdraw an element from inventory. It only performs quantity 
        check to avoid 'critical race' issues
            
        """
        with transaction.atomic():
            inventory_item = Inventory.objects.select_for_update().get(id=inventory_id)
            if qta < 0:
                InventoryServices.is_sufficient(inventory_item, -qta)
            inventory_item.quantity += qta
            inventory_item.save()
            
 