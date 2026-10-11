from django.db import transaction
from datetime import datetime, timezone

# MODELS
from report.models import Operation

# EXCEPTIONS
from core.exceptions import BusinessLogicError


class OperationServices:

    VALID_CREATION_STATUS = (
        Operation.Operation_status.DRAFT,     # administrator
        Operation.Operation_status.PLANNED,   # administrator
        Operation.Operation_status.RUNNING,   # technician

    )

    PLANNING_STATUS = (
        Operation.Operation_status.DRAFT,     # administrator
        Operation.Operation_status.PLANNED,   # administrator
    )

    DRAFT_STATUS = Operation.Operation_status.DRAFT

    #########################
    #     UTILS METHODS     #
    #########################

    @staticmethod
    def is_initial_status_valid(operation_instance):
        """
            valid Operation's initial status:
                - DRAFT (only admins)
                - PLANNED (only admins)
                - RUNNING (only technicians)
        """


        # check if the initial status is valid
        if operation_instance.status not in OperationServices.VALID_CREATION_STATUS:
            raise BusinessLogicError("Operation invalid status: {operation_instance.status}")

        # Check if the initial status implies technician assigned at the task
        if operation_instance.status is OperationServices.DRAFT_STATUS:
            if not operation_instance.technician_fk:
                raise BusinessLogicError("Technicians are required")
        return True



    #########################
    #  VALIDATION METHODS   #
    #########################

    @staticmethod
    def validate_operation_instance(operation_instance):
        """Validate an operation creation
        what does it check:
            - operation status is PLANNED, RUNNING or DRAFT
            - if is PLANNED or RUNNING, technician_fk can't be None
            - date shouldn't be in the past (not yet implemented)
        """
        ReportServices.is_initial_status_valid(report_instance)
        return True


    #########################
    #  APPLICATION METHODS  #
    #########################

    def create_operation(operation_instance):
        operation_instance.save()
        return True
