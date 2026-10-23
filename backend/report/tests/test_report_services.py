import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import datetime
from django.utils import timezone

# EXCEPTIONS
from core.exceptions import BusinessLogicError

# MODELS
from report.models import Report
from report.models import Operation
from administration.models import (
    Customer_records,
    Machinery_records,
    HR_records,
)

# METHODS
from report.services.report_services import ReportServices

User = get_user_model()

@pytest.mark.django_db
class TestReportServices:

    @pytest.fixture
    def sample_user(db):
        """User WITHOUT supervisor permissions"""
        return User.objects.create_user(username="clerk", is_active=True)

    @pytest.fixture
    def sample_technician_orm(self, sample_user):
        hr_record_orm = HR_records.objects.create(
            name="Turi",                               #[cite: 2] Campo CharField(max_length=50)
            surname="D'avola",                            #[cite: 2] Campo CharField(max_length=50)
            date_birth=datetime.date(1985, 6, 15),      #[cite: 2] Campo DateField
            associated_user=sample_user                        #[cite: 2] OneToOneField verso AUTH_USER_MODEL
        )
        return hr_record_orm

    @pytest.fixture
    def sample_customer_orm(self):
        customer_orm = Customer_records.objects.create(
            desc="ACME Industrial S.r.l.",
            iva="12345678901"
        )
        return customer_orm

    @pytest.fixture
    def sample_machinery_orm(self):
        machinery_orm = Machinery_records.objects.create(
            brand="Bosch Rexroth",
            model="Hydraulic Pump HP-500"
        )
        return machinery_orm

    @pytest.fixture
    def sample_operation_dict(self, sample_technician_orm):
        mock_operation_payload = {
            "title": "Sostituzione guarnizione flangiata e test pressione",
            "instructions": "Utilizzare guarnizione in PTFE e serrare a 45Nm.",
            "status": "RUNNING",  # Scelta tra: 'DRAFT', 'PLANNED', 'RUNNING', 'PAUSED', 'COMPLETED', 'CANCELLED'
            "scheduled_datetime": "2026-10-24T08:30:00Z",
            "start_now": False,
            "technicians": [sample_technician_orm],
        }
        return mock_operation_payload

    @pytest.fixture
    def sample_report_dict(self, sample_operation_dict, sample_customer_orm, sample_machinery_orm):
        """
        Report dict -> ReportService methods attribute
        """

        mock_report_payload = {
            # Campi identificativi e anagrafici del Report
            "code": "REP-2026-0001",
            "customer_fk": sample_customer_orm,  # ID del record cliente (Customer_records)
            "machinery_fk": sample_machinery_orm,  # ID del macchinario (Machinery_records, opzionale)

            # Classificazione
            "priority": "HIGH",  # Scelta tra: 'LOW', 'MED', 'HIGH', 'EMG'
            "status": None,    # Scelta tra: 'DRAFT', 'PLANNED', 'OPEN', 'ON_HOLD', 'COMPLETED', 'CLOSED', 'CANCELLED'

            # Testi e Note
            "title": "Manutenzione straordinaria pompa idraulica Linea 3",
            "description": "Rilevata perdita d'olio dal raccordo principale durante il turno mattutino.",
            "internal_notes": "Intervenire tempestivamente prima del cambio turno.",

            # Metadati temporali
            "date_scheduled": "2026-10-24T08:00:00Z",

            # start operation (nested serializer)
            "operation": sample_operation_dict,
            "publish_now": True,

        }
        return mock_report_payload

    @pytest.fixture
    def sample_report_orm(self, sample_customer_orm, sample_machinery_orm):
        return Report.objects.create(
            code="REP-2026-0001",
            customer_fk=sample_customer_orm,          #[cite: 1] Istanza obbligatoria di Customer_records[cite: 2]
            machinery_fk=sample_machinery_orm,        #[cite: 1] Istanza opzionale di Machinery_records[cite: 2]
            priority="HIGH",               #[cite: 1] Valori ammessi: LOW, MED, HIGH, EMG
            status="OPEN",                 #[cite: 1] Valori ammessi: DRAFT, PLANNED, OPEN, ON_HOLD, COMPLETED, CLOSED, CANCELLED
            title="Manutenzione straordinaria pompa idraulica Linea 3",
            description="Rilevata perdita d'olio dal raccordo principale durante il turno mattutino.",
            internal_notes="Intervenire prima del cambio turno.",
            created_by=None                #[cite: 1] Istanza dell'utente che crea il report
        )

    #########################
    #      Utils tests      #
    #########################

    def test_report_dict_to_ORM(self, sample_report_dict):
        report_orm = ReportServices.get_report_ORM(sample_report_dict)
        assert report_orm.status is sample_report_dict.get('status')

    def test_operation_dict_to_ORM(self, sample_operation_dict):
            operation_orm = ReportServices.get_operation_ORM(sample_operation_dict)
            assert operation_orm.status is sample_operation_dict.get('status')


    ##################################################
    ##########     PUBLIC METHOD TESTS     ###########
    ##################################################

    ######################
    #### empty report ####
    ######################

    def test_new_report_success__open_empty(self, sample_report_dict):
        sample_report_dict['operation'] = None
        sample_report_dict['publish_now'] = True

        ReportServices.new_empty_report(sample_report_dict)

        assert Report.objects.filter(code=sample_report_dict['code']).exists() # REP-2026-0001
        report_in_db = Report.objects.get(code=sample_report_dict['code'])
        assert report_in_db.status == "OPEN"

    def test_new_report_success__draft_empty(self, sample_report_dict):
        sample_report_dict['operation'] = None
        sample_report_dict['publish_now'] = False

        ReportServices.new_empty_report(sample_report_dict)

        assert Report.objects.filter(code=sample_report_dict['code']).exists() # REP-2026-0001
        report_in_db = Report.objects.get(code=sample_report_dict['code'])
        assert report_in_db.status == "DRAFT"

    def test_new_report_success__supervisor(self, sample_report_dict):
        sample_report_dict['operation'] = None
        sample_report_dict['status'] = "CANCELLED"

        ReportServices.new_empty_report(sample_report_dict)

        report_in_db = Report.objects.get(code=sample_report_dict['code'])
        assert report_in_db.status == "CANCELLED"

    ######################
    ### new operation ####
    ######################

    def test_new_operation_success__start_now(self, sample_report_orm, sample_operation_dict):
        sample_operation_dict['status'] = None
        sample_operation_dict['report_fk'] = sample_report_orm
        sample_operation_dict['start_now'] = True
        sample_operation_dict['scheduled_datetime'] = None

        operation_id = ReportServices.add_operation_to_report(sample_operation_dict).pk

        operation = Operation.objects.get(id=operation_id)
        assert operation.status == "RUNNING"

    def test_new_operation_success__planned(self, sample_report_orm, sample_operation_dict):
        sample_operation_dict['status'] = None
        sample_operation_dict['report_fk'] = sample_report_orm
        sample_operation_dict['start_now'] = False

        operation_id = ReportServices.add_operation_to_report(sample_operation_dict).pk

        operation = Operation.objects.get(id=operation_id)
        assert operation.status == "PLANNED"

    def test_new_operation_success__draft(self, sample_report_orm, sample_operation_dict):
        sample_operation_dict['status'] = None
        sample_operation_dict['report_fk'] = sample_report_orm
        sample_operation_dict['scheduled_datetime'] = None

        operation_id = ReportServices.add_operation_to_report(sample_operation_dict).pk

        operation = Operation.objects.get(id=operation_id)
        assert operation.status == "DRAFT"

    def test_new_operation_failure__scheduled_and_start_now(self, sample_report_orm, sample_operation_dict):
        sample_operation_dict['status'] = None
        sample_operation_dict['report_fk'] = sample_report_orm
        sample_operation_dict['start_now'] = True

        with pytest.raises(BusinessLogicError):
            ReportServices.add_operation_to_report(sample_operation_dict)

    def test_new_operation_failure__report_closed(self, sample_report_orm, sample_operation_dict):
        sample_operation_dict['status'] = None
        sample_report_orm.status = "CLOSED"
        sample_operation_dict['report_fk'] = sample_report_orm

        with pytest.raises(BusinessLogicError):
            ReportServices.add_operation_to_report(sample_operation_dict)

    ############################
    #### operation + report ####
    ############################

    def test_report_and_operation_success__quickstart(self, sample_report_dict, sample_operation_dict):
        # set status to none
        sample_report_dict['status'] = None
        sample_operation_dict['status'] = None

        # set flags
        sample_report_dict['publish_now'] = True
        sample_operation_dict['start_now'] = True
        sample_operation_dict['scheduled_datetime'] = None

        result = ReportServices.new_report_with_operation(sample_report_dict, sample_operation_dict)
        operation_id = result['operation'].pk
        report_id = result['report'].pk

        operation = Operation.objects.get(id=operation_id)
        report = Report.objects.get(report_id=report_id)

        assert operation.status == "RUNNING"
        assert report.status == "OPEN"

    def test_report_and_operation_success__draft_and_planned_operation(self, sample_report_dict, sample_operation_dict):
        # set status to none
        sample_report_dict['status'] = None
        sample_operation_dict['status'] = None

        # set flags
        sample_report_dict['publish_now'] = False
        sample_operation_dict['start_now'] = False
        # scheduled datetime set

        result = ReportServices.new_report_with_operation(sample_report_dict, sample_operation_dict)
        operation_id = result['operation'].pk
        report_id = result['report'].pk

        operation = Operation.objects.get(id=operation_id)
        report = Report.objects.get(report_id=report_id)

        assert operation.status == "PLANNED"
        assert report.status == "DRAFT"

    def test_report_and_operation_success__planned_and_planned_operation(self, sample_report_dict, sample_operation_dict):
        # set status to none
        sample_report_dict['status'] = None
        sample_operation_dict['status'] = None

        # set flags
        sample_report_dict['publish_now'] = True
        sample_operation_dict['start_now'] = False
        # scheduled datetime set

        result = ReportServices.new_report_with_operation(sample_report_dict, sample_operation_dict)
        operation_id = result['operation'].pk
        report_id = result['report'].pk

        operation = Operation.objects.get(id=operation_id)
        report = Report.objects.get(report_id=report_id)

        assert operation.status == "PLANNED"
        assert report.status == "PLANNED"

    def test_report_and_operation_success__open_and_draft_operation(self, sample_report_dict, sample_operation_dict):
        # set status to none
        sample_report_dict['status'] = None
        sample_operation_dict['status'] = None

        # set flags
        sample_report_dict['publish_now'] = True
        sample_operation_dict['start_now'] = False
        sample_operation_dict['technicians'] = None
        # scheduled datetime set

        result = ReportServices.new_report_with_operation(sample_report_dict, sample_operation_dict)
        operation_id = result['operation'].pk
        report_id = result['report'].pk

        operation = Operation.objects.get(id=operation_id)
        report = Report.objects.get(report_id=report_id)

        assert operation.status == "DRAFT"
        assert report.status == "OPEN"
