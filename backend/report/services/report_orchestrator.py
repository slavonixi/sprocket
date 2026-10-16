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



    #########################################
    #    Permissions Validation Methods     #
    #########################################

    def is_user_auth(user):
        if not user or not user.is_authenticated:
             raise BusinessLogicError(_("You must be authenticated to perform this operation"))
        return True

    #    Report

    @staticmethod
    def is_report_initial_status_valid(user, report_status):
        if user.has_perm('can_override_reports'):
            # If the user is a Supervisor he can create reports in whatever status
            pass
        else:
            if report_status is [Report.ReportStatus.DRAFT, Report.ReportStatus.PLANNED]:
                if not user.has_perm('report.can_draft_reports'):
                    raise BusinessLogicError('You do not have the permissions to draft a report')
            elif report is Report.ReportStatus.OPEN:
                pass
            else:
                raise BusinessLogicError('Invalid report initial status')
        return True


    #   Operation

    @staticmethod
    def is_operation_initial_status_valid(user, OperationStatus):
        """
            - Technicians can create RUNNING operations
            - Admins can create PLANNED operations
        """
        # check if the initial status is valid
        if status is Operation.OperationStatus.PLANNED:
            # Only admins can create a PLANNED operation
            if not user.has_perm('report.can_plan_operations'):
                raise BusinessLogicError(_('You have not the permissions to plan an operation'))
        elif status is Operation.OperationStatus.RUNNING:
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
        ReportOrchestrator.is_user_auth(user)
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
