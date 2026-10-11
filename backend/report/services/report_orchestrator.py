# SERVICES
from report.services.operation_services import OperationServices 
from report.services.report_services import ReportServices 
from django.db import transaction


# MODELS
from report.models import Operation, Report

# EXCEPTIONS
from report.exceptions import (
    PermissionDenied,
    IllegalReportStatus,
)

class ReportOrchestrator:

    REPORT_INITIAL_STATUS = (
        Report.Report_status.DRAFT,
        Report.Report_status.OPEN,
    )

    #########################################
    #    Permissions Validation Methods     #
    #########################################

    @staticmethod
    def is_report_initial_status_valid(user, report_instance):
        status = report_instance.status
        # check if the status is in the valid initial status
        if status in ReportOrchestrator.REPORT_INITIAL_STATUS:
            # the status is valid, but we have to check
            # if the user can 'draft' a report
            if not user.has_perm('report.can_draft_report'):
                if status is Report.Report_status.DRAFT:
                    raise PermissionDenied('draft_report')
            return True
        else:
            raise IllegalReportStatus(status)

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

    @staticmethod
    def validate_create_report(user, report_instance):
        ReportOrchestrator.is_report_initial_status_valid(user, report_instance)
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

            