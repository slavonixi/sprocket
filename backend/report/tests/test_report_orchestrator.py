import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from unittest.mock import patch


# EXCEPTIONS
from report import exceptions

# MODELS
from report.models import Operation
from administration.models import Customer_records

# METHODS
from report.services.report_orchestrator import ReportOrchestrator


User = get_user_model()

@pytest.fixture
def supervisor_user(db):
    """Supervisor/administrator user who can only plan or draft operations"""
    user = User.objects.create_user(username="supervisor", is_active=True)
    
    # Assign custom permission
    content_type = ContentType.objects.get_for_model(Operation)
    perm = Permission.objects.get(codename="can_plan_operations", content_type=content_type)
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def technician_user(db):
    """Technician user who can only start operations"""
    user = User.objects.create_user(username="technician", is_active=True)
    
    # Assign custom permission
    content_type = ContentType.objects.get_for_model(Operation)
    perm = Permission.objects.get(codename="can_run_operations", content_type=content_type)
    user.user_permissions.add(perm)
    return user

@pytest.mark.django_db
class TestReportOrchestrator:
    
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

    @patch('report.services.report_orchestrator.OperationServices.validate_operation_instance')
    def test_supervisor_can_plan_operation(self, supervisor_user, sample_operation):
        sample_operation.status = Operation.Operation_status.PLANNED
        assert ReportOrchestrator.validate_create_operation(supervisor_user, sample_operation) is True

    @patch('report.services.report_orchestrator.OperationServices.validate_operation_instance')
    def test_supervisor_cannot_run_operation(self, mock_validate, supervisor_user, sample_operation):
        sample_operation.status = Operation.Operation_status.RUNNING
        with pytest.raises(exceptions.PermissionDenied):
            ReportOrchestrator.validate_create_operation(supervisor_user, sample_operation)

    @patch('report.services.report_orchestrator.OperationServices.validate_operation_instance')
    def test_technician_can_run_operation(self, mock_validate, technician_user, sample_operation):
        sample_operation.status = Operation.Operation_status.RUNNING
        assert ReportOrchestrator.validate_create_operation(technician_user, sample_operation) is True

    @patch('report.services.report_orchestrator.OperationServices.validate_operation_instance')
    def test_technician_cannot_plan_operation(self, mock_validate, technician_user, sample_operation):
        sample_operation.status = Operation.Operation_status.PLANNED
        with pytest.raises(exceptions.PermissionDenied):
            ReportOrchestrator.validate_create_operation(technician_user, sample_operation)

    