# SERVICES
from report.services.operation_services import OperationServices 
from report.services.report_services import ReportServices 
from django.db import transaction


# MODELS
from report.models import Operation, Report

# EXCEPTIONS
from report.exceptions import PermissionDenied

class ReportOrchestrator:

    #########################################
    #    Permissions Validation Methods     #
    #########################################

    def can_start_operation(user, operation_instance):
        if operation_instance.status == Operation.Operation_status.RUNNING:
            if not user.has_perm('report.can_run_operations'):
                raise PermissionDenied(op='run_operation')
        return True

    def can_plan_operations(user, operation_instance):
        if operation_instance.status in OperationServices.PLANNING_STATUS:
            if not user.has_perm('report.can_plan_operations'):
                raise PermissionDenied(op='plan_operation')
        return True
        

    #########################
    #  VALIDATION METHODS   #
    #########################
    

    @staticmethod
    def validate_create_operation(user, operation_instance):
        """
            When creating an operation it checks:
                - operation instance is valid
                - if you are a technician
        """

        # checks if the operation instance is valid
        OperationServices.validate_operation_instance(operation_instance)
        # if is a planning, check if is an admin
        ReportOrchestrator.can_plan_operations(user, operation_instance)
        # if is a starting, check if is a technician 
        ReportOrchestrator.can_start_operation(user, operation_instance)
        return True


    #########################
    #  APPLICATION METHODS  #
    #########################

    @staticmethod
    def orchestrate_operation_creation(user, operation_instance):
        # assigning user to 'created_by' field
        operation_instance.created_by = user

        with transaction.atomic():
             
            # report creation  logic
            OperationServices.create_operation(user, operation_instance)

            