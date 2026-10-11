from core.exceptions import BusinessLogicError
from django.db import transaction
from inventory.models import Movement


class MovementServices:


    #########################
    ## Validation methods ###
    #########################

    @staticmethod
    def is_not_zero_or_negative(qty):
        if qty > 0:
            return True
        else:
            raise BusinessLogicError("The quantity must be > 0")

    @staticmethod
    def validate_movement_item(movement_item):
        """ Called by InventoryOrchestrator to let the serializer validate a
            Movement item
        """
        MovementServices.is_not_zero_or_negative(movement_item.quantity)
        return True

    #########################
    ##    Utils methods    ##
    #########################

    def get_signed_qty(movement_item: Movement):
        """
            Tells if the value to apply to the stock is positive or negative
            depends on operation_direction (inbound or outbound)
        """
        if movement_item.operation_direction == Movement.OperationDirection.INBOUND:
            return movement_item.quantity  #return positive quantity
        elif movement_item.operation_direction == Movement.OperationDirection.OUTBOUND:
            return -movement_item.quantity #return negtive quantity
        else:
            raise BusinessLogicError("Movement.direction is invalid")

    #########################
    ## Application methods ##
    #########################

    @staticmethod
    def create_movement(movement_item):
        movement_item.save()
        return movement_item

    # DELETE AND UPDATE MOVEMENTs IS FORBIDDEN
