import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timezone

# EXCEPTIONS
from report import exceptions

# MODELS
from report.models import Report
from administration.models import Customer_records

# METHODS
from report.services.report_services import ReportServices


@pytest.mark.django_db
class TestReportServices:

    @pytest.fixture
    def sample_customer(self):
        return Customer_records.objects.create(
            desc = 'test customer 1'
        )

    @pytest.fixture
    def sample_report(self, sample_customer):
        """Creates an 'OPEN' sample Report instsance, editable in the other methods"""
        return Report.objects.create(
            desc = 'test report',
            customer_fk = sample_customer,
            status = Report.Report_status.OPEN,
        )

    #########################
    #         TESTS         #
    #########################

    def test_report_creation_fails_if_status_is_illegal(self, sample_report):
        with pytest.raises(exceptions.IllegalReportStatus):
            ReportServices.is_initial_status_valid(
                sample_report
            )
    
    def test_initial_status_is_valid(self, sample_report):
        sample_report.status = Report.Report_status.DRAFT
        assert ReportServices.is_initial_status_valid(sample_report) == True

    def test_invalid_date_close(self, sample_report):
        sample_report.date_close = datetime.now()
        with pytest.raises(exceptions.IllegalDateField):
            ReportServices.are_dates_valid(sample_report)

    # Tests [open_date = none] vs [open_date = smth] 
    #                   |                  |
    #                   |                  |
    #                  admins            technic.
    #
    #         SHOULD BE DONE IN TEST_ORCHESTRATOR