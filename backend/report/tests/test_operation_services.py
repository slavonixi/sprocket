import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# EXCEPTIONS
from report import exceptions

# MODELS
from report.models import Operation
from administration.models import Customer_records

# METHODS
from report.services.operation_services import OperationServices


@pytest.mark.django_db
class TestReportServices:

    # @pytest.fixture
    # def sample_customer(self):
    #     return Customer_records.objects.create(
    #         desc = 'test customer 1'
    #     )

    @pytest.fixture
    def sample_operation(self):
        return Operation.objects.create(
            desc = 'test Operation',
            status = Operation.Operation_status.DRAFT,
            date = timezone.now(),
        )

    #########################
    #         TESTS         #
    #########################

    def test_operation_initial_status_is_valid(self, sample_operation):
        assert OperationServices.is_initial_status_valid(sample_operation) is True