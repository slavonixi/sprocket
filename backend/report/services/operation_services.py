from django.db import transaction
from datetime import datetime, timezone

# MODELS
from report.models import Operation

# EXCEPTIONS
from core.exceptions import BusinessLogicError


class OperationServices:



    #########################
    #     UTILS METHODS     #
    #########################

    def is_date_valid(operation_instance : Operation):
        pass



    #########################
    #  VALIDATION METHODS   #
    #########################

    @staticmethod
    def validate_operation_instance(operation_instance):
        # check if the date is valid
        OperationServices.is_date_valid(operation_instance)

        return True


    #########################
    #  APPLICATION METHODS  #
    #########################

    def create_operation(operation_instance):
        operation_instance.save()
        return True
