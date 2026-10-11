from django.db import transaction
from datetime import datetime, timezone
from core.exceptions import BusinessLogicError


# MODELS
from report.models import Report



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
                - Report is OPEN but no date_open is provided
        """
        status = report_instance.status
        date_open = report_instance.date_open

        if date_open:
            if status is Report.Report_status.DRAFT:
                # a DRAFT report can't have a date_open
                raise BusinessLogicError("draft reports have not date")
        elif status is Report.Report_status.OPEN:
            # an OPEN report must have a date_open
            raise BusinessLogicError("Open reports must have a date")

        if report_instance.date_close:
            # a new report mustn't have a date_close
            raise BusinessLogicError("A new report can't have a date close")
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
