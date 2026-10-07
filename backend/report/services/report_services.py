from django.db import transaction
from datetime import datetime, timezone

# MODELS
from report.models import Report

# EXCEPTIONS
from report.exceptions import IllegalReportStatus, IllegalDateField


class ReportServices: 

    #########################
    #     UTILS METHODS     #
    #########################

    @staticmethod
    def is_initial_status_valid(report_instance):
        """
            valid initial status:
                - DRAFT (for admins)
                - RUNNING (for technicians)
        """
        valid_creation_status = (
            Report.Report_status.DRAFT,     # administrator
            Report.Report_status.RUNNING    # technician

        )
        if report_instance.status not in valid_creation_status:
            raise IllegalReportStatus(report_instance.status)
        return True

    @staticmethod
    def are_dates_valid(report_instance):
        if report_instance.date_close:
            raise IllegalDateField(report_instance.date_close)
        return True

    def customer_isset(report_instance : Report):
        if not report_instance.customer_fk:
            raise CustomerIsNone
        return True
    #########################
    #  VALIDATION METHODS   #
    #########################


    def validate_create_report(report_instance : Report):
        """Validate any report instance (used for report creation)"""
        ReportServices.is_initial_status_valid(report_instance)
        ReportServices.are_dates_valid(report_instance)
        ReportServices.customer_isset(report_instance)
        
        
    #########################
    #  APPLICATION METHODS  #
    #########################

    