import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# EXCEPTIONS
from core.exceptions import BusinessLogicError

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
            status = Report.ReportStatus.DRAFT,
        )

    #########################
    #         TESTS         #
    #########################

    # HAPPY CASES

    def test_draft_report_with_no_dates(self, sample_report):
        assert ReportServices.are_dates_valid(sample_report) is True

    def test_open_report_with_date_open(self, sample_report):
        # set date_open and status
        sample_report.status = Report.ReportStatus.OPEN
        sample_report.date_open = timezone.now()
        assert ReportServices.are_dates_valid(sample_report) is True



    # EXCEPTIONS AND ERRORS

    def test_invalid_report_with_close_date(self, sample_report):
        # set date_close
        sample_report.date_close = timezone.now()

        with pytest.raises(BusinessLogicError):
            ReportServices.are_dates_valid(sample_report)

    def test_invalid_open_report_with_no_open_date(self, sample_report):
        # set status open
        sample_report.status = Report.ReportStatus.OPEN
        with pytest.raises(BusinessLogicError):
            ReportServices.are_dates_valid(sample_report)
