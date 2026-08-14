from inventory import exceptions
from django.db import transaction
from inventory.models import Movement
from rest_framework.exceptions import APIException # pyright: ignore


class MovementServices:


    #########################
    ## Validation methods ###
    #########################

    @staticmethod
    def is_not_zero_or_negative(qty):
        if qty > 0:
            return True
        else:
            raise exceptions.MovementQtyIsZeroOrNegativeError()

    @staticmethod
    def validate_movement_item(movement_item):
        """ Called by InventoryOrchestrator to let the serializer validate a 
            Movement item
        """
        MovementServices.is_not_zero_or_negative(movement_item.qty)
        return True

    #########################
    ##    Utils methods    ##
    #########################

    def get_signed_qty(movement_item: Movement):
        """
            Tells if the value to apply to the stock is positive or negative
            depending on operation_direction (inbound or outbound)
        """
        if movement_item.operation_direction == Movement.OperationDirection.INBOUND:
            return movement_item.qty  #return positive qty
        elif movement_item.operation_direction == Movement.OperationDirection.OUTBOUND:
            return -movement_item.qty #return negtive qty
        else:
            raise exceptions.IllegalOperationValue(
                op="movement_create", 
                illegal_value=movement_item.operation_direction
            )

    #########################
    ## Application methods ##
    #########################

    @staticmethod
    def create_movement(movement_item):
        movement_item.save()
        return movement_item

    # DELETE AND UPDATE MOVEMENT IS FORBIDDEN