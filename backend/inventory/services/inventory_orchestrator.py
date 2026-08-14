from inventory.services.inventory_services import InventoryServices
from inventory.services.movement_services import MovementServices
from inventory import exceptions
from django.db import transaction
from api import tasks
from celery import Celery
import traceback
import sys
from rest_framework.exceptions import APIException #type: ignore

class InventoryOrchestrator:
    """It able API to performs operation through Inventory and Movement models.
        It is used for both validation and implementation methods

        VALIDATIONS:
            validations methods are called separately by serializers validate()
            built-in method. Often operations needs to validate the status of  
            both the Movement item and the Inventory item.
    """ 

    #############################
    #    Validation Methods     #
    #############################

    @staticmethod
    def validate_movement_create(inventory_item, movement_item):

        qty = movement_item.qty
        try:
            MovementServices.validate_movement_item(movement_item)
            InventoryServices.validate_stock_operation(inventory_item, qty)
        except exceptions.InventoryError:
            pass
