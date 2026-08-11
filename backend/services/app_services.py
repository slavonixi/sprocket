from inventory.services.inventory_services import InventoryServices
from api import exceptions
from django.db import transaction
from api import tasks
from celery import Celery
from api import exceptions
import traceback
import sys
from rest_framework.exceptions import APIException #type: ignore

class ServiceOrchestrator:
    """To perform cross-modules operations.
        
    
    """
    @staticmethod
    def validate_inventory_withdraw(inventory_item, qty):
        try:
            InventoryServices.validate_stock_reduction(inventory_item, qty)
        except APIException as e:
            res = e.detail
            tasks.database_celery_log.delay(res)
            raise e

    @staticmethod
    def validate_withdraw_update(inventory_item, old_qta, new_qta):
        """Check if updated data are valid to withdraw or restore 
           the items, performing other routine validations for each
           operation

        
        """

        

        try:
            InventoryServices.compare_qty(old_qta, new_qta)
            delta = old_qta-new_qta
            if delta < 0: #is a WITHDRAW 
                #What this methods do:
                # -check if there are enough items to remove
                # -check that the withdrawing value format is correct

                #delta has to be >0 for validate_stock_reduction()
                InventoryServices.validate_stock_reduction(inventory_item, -delta)
                InventoryServices.validate_stock_value(inventory_item, delta)
            else: #is a RESTORE (update or delete a previous operation)
                #(If we are here, it means that the operation
                # has just to **ADD** items, not withdraw (remove))
                # -  So Just check that value is correct
                InventoryServices.validate_stock_value(inventory_item, delta)
        except APIException as e:
            res = e.detail
            tasks.database_celery_log.delay(res)
            raise e
        return True

    @staticmethod
    def withdraw_inventory(inventory_id, qta_to_remove):
        """Create a new withdraw operation (just to reduce stock)
        
        """
        try:
            with transaction.atomic():
                # Esegue lo scarico dell'Inventory
                res = InventoryServices.apply_to_stock(inventory_id, -qta_to_remove)
        except Exception as e:
            res = e.detail    
            raise e
        finally:
            tasks.database_celery_log.delay(res)

    def update_withdraw(inventory_id, old_qta, new_qta):
        """Update an inventory-withdraw opertaion
        
            e.g.    1) withdraw 7 items (0 items left)
            update: 2) withdraw 6 instead of 7 (restore 1 item in inventory)
        """
        if old_qta != new_qta:
            adjust_qta = old_qta - new_qta 
            with transaction.atomic():
                try:
                    with transaction.atomic():
                    #add or remove the difference
                        InventoryServices.apply_to_stock(inventory_id, adjust_qta)
                except APIException as e:
                    res = e.detail
                    tasks.database_celery_log.delay(res)
                    raise e

    def delete_withdraw(inventory_id, quantity_to_restore):
        """Delete a withdraw operation (and so restore the items in inventory)

        """
        with transaction.atomic():
            try:
                with transaction.atomic():
                    InventoryServices.apply_to_stock(inventory_id, quantity_to_restore)
            except APIException as e:
                res = e.detail
                tasks.database_celery_log.delay(res)
                raise e
                