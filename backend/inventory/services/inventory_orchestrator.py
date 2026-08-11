from inventory.services.inventory_services import InventoryServices
from inventory.services.movement_services import MovementServices
from api import exceptions
from django.db import transaction
from api import tasks
from celery import Celery
from api import exceptions
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

    