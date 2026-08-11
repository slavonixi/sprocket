from api import exceptions
from django.db import transaction
from inventory.models import Movement
from rest_framework.exceptions import APIException # pyright: ignore


class MovementServices:

    @staticmethod
    def create_movement(movement_item):
        movement_item.save()
        return movement_item

    @staticmethod
    def update_movement(movement_id, new_qty):
         with transaction.atomic():
            movement_item = Movement.objects.select_for_update().get(id=movement_id)
            movement_item.qty = new_qty
            movement_item.save()
            return movement_item

    @staticmethod
    def delete_movement(movement_item):
        movement_item.delete()
        return True