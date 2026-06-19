from .inventory_services import InventoryServices
from test1 import exceptions
from django.db import transaction

class ServiceOrchestrator:


    @staticmethod
    def withdraw_inventory(inventory_id, qta_to_remove):
        with transaction.atomic():
            InventoryServices.apply_stock_reduction(inventory_id, qta_to_remove)

    def update_withdraw(inventory_id, old_qta, new_qta):
        if old_qta != new_qta:
            adjust_qta = old_qta - new_qta
            with transaction.atomic():
                try:
                    InventoryServices.apply_to_stock(inventory_id, adjust_qta)
                except exceptions.InsufficientStockError:
                    raise exceptions.InsufficientStockForUpdate()
        
    def delete_withdraw(inventory_id, quantity_to_restore):
        with transaction.atomic():
            InventoryServices.apply_to_stock(inventory_id, quantity_to_restore)