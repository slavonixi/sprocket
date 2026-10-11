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
    def are_dates_valid(report_instance : Report):
        """
            validate dates and raise an error if:
                - date open is set but report is a DRAFT
                - date close is set 
        """
        status = report_instance.status
        date_open = report_instance.date_open
        
        if status is Report.Report_status.DRAFT:
            if date_open:
                raise DateError
        if report_instance.date_close:
            raise DateError
        return True
        
        
    #########################
    #  VALIDATION METHODS   #
    #########################

    @staticmethod
    def validate_new_report_instance(report_instance : Report):
        ReportServices.are_dates_valid(report_instance)
        
        
        
    #########################
    #  APPLICATION METHODS  #
    #########################

    