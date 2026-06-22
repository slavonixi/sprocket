from .inventory_services import InventoryServices
from api import exceptions
from django.db import transaction

class ServiceOrchestrator:
    """To perform cross-modules operations.
        
    
    """

    @staticmethod
    def withdraw_inventory(inventory_id, qta_to_remove):
        """Create a new withdraw operation (just to reduce stock)
        
        """
        with transaction.atomic():
            InventoryServices.apply_to_stock(inventory_id, -qta_to_remove)

    def update_withdraw(inventory_id, old_qta, new_qta):
        """Update an inventory-withdraw opertaion
        
            e.g. withdraw 7 items 
            update: withdraw 6 (restore 1 item in inventory)
        """
        if old_qta != new_qta:
            adjust_qta = old_qta - new_qta 
            with transaction.atomic():
                try:
                    #add or remove the difference
                    InventoryServices.apply_to_stock(inventory_id, adjust_qta)
                except exceptions.InsufficientStockError:
                    raise exceptions.InsufficientStockForUpdate()
        
    def delete_withdraw(inventory_id, quantity_to_restore):
        """Delete a withdraw operation (and so restore the items in inventory)

        """
        with transaction.atomic():
            InventoryServices.apply_to_stock(inventory_id, quantity_to_restore)