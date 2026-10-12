# SERVICES
from report.services.operation_services import OperationServices
from report.services.report_services import ReportServices
from django.db import transaction


# MODELS
from report.models import (
    Report,
    Operation,
)

# EXCEPTIONS
from core.exceptions import BusinessLogicError

class ReportOrchestrator:

    REPORT_INITIAL_STATUS = (
        Report.Report_status.DRAFT,
        Report.Report_status.OPEN,
    )

    OPERATION_INITIAL_STATUS = (
        Operation.Operation_status.PLANNED,
        Operation.Operation_status.RUNNING,
    )


    #########################################
    #    Permissions Validation Methods     #
    #########################################

    @staticmethod
    def is_report_initial_status_valid(user, report_status):
        # check if the status is in the valid initial status
        if report_status in ReportOrchestrator.REPORT_INITIAL_STATUS:
            # the report_status is valid, but we have to check
            # if the user can 'draft' a report
            if not user.has_perm('report.can_draft_report'):
                if status is Report.Report_status.DRAFT:
                    raise BusinessLogicError(_('You have not the permission to draft a report'))
            return True
        else:
            raise BusinessLogicError(_("The report's initial status is not valid"))

    @staticmethod
    def is_operation_initial_status_valid(user, operation_status):
        """
            - Technicians can create RUNNING operations
            - Admins can create PLANNED operations
        """
        # check if the initial status is valid
        if status is Operation.Operation_status.PLANNED:
            # Only admins can create a PLANNED operation
            if not user.has_perm('report.can_plan_operations'):
                raise BusinessLogicError(_('You have not the permissions to plan an operation'))
        elif status is Operation.Operation_status.RUNNING:
            # Only technicians can create RUNNING operations
            if not user.has_perm('report.can_run_operations'):
                raise BusinessLogicError(_('You have not the permissions to run an operation'))
        else:
            raise BusinessLogicError(_("The operation's initial status is not valid"))
        return True

    #########################
    #  VALIDATION METHODS   #
    #########################


    @staticmethod
    def validate_create_operation(user, operation_instance):
        """

        """
        # check if the initial status is valid
        ReportOrchestrator.is_operation_initial_status_valid(user, operation_instance.status)
        OperationServices.validate_create_operation(operation_instance)

        return True

    @staticmethod
    def validate_create_report(user, report_instance):
        ReportOrchestrator.is_report_initial_status_valid(user, report_instance.status)
        ReportServices.validate_new_report_instance(report_instance)

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
