from django.db import transaction
from datetime import datetime, timezone

# MODELS
from report.models import Report

# EXCEPTIONS
from report.exceptions import (
    IllegalReportStatus,
    DateError,
)


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
                raise DateError(date_open)
        else if status is Report.Report_status.OPEN:
            # an OPEN report must have a date_open
            raise DateError()

        if report_instance.date_close:
            # a new report mustn't have a date_close
            raise DateError()
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
