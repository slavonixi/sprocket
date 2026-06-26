from api import exceptions
from django.db import transaction
from api.models import Inventory
from api.models import Inv_masterdata
from api.models import MeasureUnit
import logging
logger = logging.getLogger('django')

class InventoryServices:

    @staticmethod
    def debug(inv_id):
        return "InventoryServices tied"
    
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
    def validate_item(inventory_item):
        """Used for validate OBJECT items MANUALLY inserted in the inventory
        
            It is different from validate_stock_value(), since this method
            is built to validate the insertion of new items
        """
        InventoryServices.check_zero_or_negative(inventory_item.quantity)
        InventoryServices.check_decimal(inventory_item)

    @staticmethod
    def check_zero_or_negative(qta):
        """check if the value is zero or negative, raise
           a NegativeOrZeroError exception.

           In some operations, negative values are forbidden.
           Zero values are forbidden in every operation.
        
        """
        if qta <= 0:
            raise exceptions.NegativeOrZeroError()


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
                raise exceptions.DecimalValueError(inventory_item.get_unit_measure())
        
        return True
    @staticmethod    
    def is_sufficient(inventory_item, qta_to_remove):
        """Check if there are enough items to withdraw.
        
           !!! Always take a positive qta_to_remove
        """
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
        """Check if the new value of a pre-existing item is valid
        
            It is different from validate_item(), since this method is built for 
            real items
        """
        InventoryServices.check_zero_or_negative(qta) 
        #check if decimal values are accepted for this item
        InventoryServices.check_decimal(inventory_item, qta)
        return True

    def validate_stock_reduction(inventory_item, qta_to_remove):
        """Perform all the required methods to check if it is possible
           to withdraw an item from inventory.
        
        """
        InventoryServices.validate_stock_value(inventory_item, qta_to_remove)
        InventoryServices.is_sufficient(inventory_item, qta_to_remove)
        

    def validate_stock_update(inventory_item, old_qta, new_qta):
        """Check if updated data are valid and withdraw or restore 
           the items, performing other routine validations for each
           operation

        
        """
        if old_qta == new_qta:
            raise exceptions.NoChangeDetectedInUpdate(new_qta)
        
        delta = old_qta-new_qta
        if delta < 0: #is a WITHDRAW
            InventoryServices.validate_stock_reduction(inventory_item, -delta)
        else: #is a RESTORE
            InventoryServices.validate_stock_value(inventory_item, delta)
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
    def apply_to_stock(inventory_id, qta): 
        """
        add the qta value of an inventory element. It performs an 
        availability check to avoid 'critical race' issues.
            
        """
        with transaction.atomic():
            inventory_item = Inventory.objects.select_for_update().get(id=inventory_id)
            if qta < 0: #if true -> withdraw | if false -> restore
                InventoryServices.is_sufficient(inventory_item, -qta)
            inventory_item.quantity += qta 
            inventory_item.save()
            
  