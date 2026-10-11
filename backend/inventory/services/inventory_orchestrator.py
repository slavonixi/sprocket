from inventory.services.inventory_services import InventoryServices
from inventory.services.movement_services import MovementServices
from core.exceptions import BusinessLogicError

from django.db import transaction
from administration import tasks
from celery import Celery
import traceback
import sys

#models
from inventory.models import Inventory
from inventory.models import Movement

class InventoryOrchestrator:
    """It able API to performs operation through Inventory and Movement models.
        It is used for both validation and implementation methods

        VALIDATIONS:
            validations methods are called separately by serializers validate()
            built-in method. Often operations needs to validate the status of
            both the Movement item and the Inventory item.
    """

    #########################################
    #    Permissions Validation Methods     #
    #########################################

    @staticmethod
    def validate_user_is_active(user):
        if not user.is_active:
            raise BusinessLogicError("User is not active")


    @staticmethod
    def validate_movement_adjustment(movement_item, user):
        if movement_item.correction_id:
            if not user.has_perm('inventory.can_adjust_movement'):
                raise BusinessLogicError("The user hasn't the permission to adjust a movement")
            else:
                return True

    @staticmethod
    def validate_can_create_movement():
        """check if the user is a technician or an administrator.
                - administrators can always create and adjust
                - technician cannot adjust. They can only create if are LISTED on the report and it is OPEN
        """

        pass

    #############################
    #    Validation Methods     #
    #############################

    @staticmethod
    def validate_movement_create(inventory_item : Inventory, movement_item : Movement, *, user):

        qty = movement_item.quantity
        InventoryOrchestrator.validate_user_is_active(user)

            # Business Rule: If this is a correction, user MUST be a Supervisor
        InventoryOrchestrator.validate_movement_adjustment(movement_item, user)
        MovementServices.validate_movement_item(movement_item)
        InventoryServices.validate_stock_operation(inventory_item, qty)

    #############################
    #    Application Methods    #
    #############################

    @staticmethod
    def create_new_movement(inventory_item : Inventory, movement_item : Movement):
        with transaction.atomic():
            movement_qty = MovementServices.get_signed_qty(movement_item)
            InventoryServices.apply_to_stock(inventory_item.id, movement_qty)
            MovementServices.create_movement(movement_item)
