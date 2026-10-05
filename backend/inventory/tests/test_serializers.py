from unittest.mock import patch
import pytest
from rest_framework.test import APIRequestFactory

from inventory.models import Inventory, Movement, Inv_masterdata, MeasureUnit
from inventory.serializers import MovementSerializer

from decimal import Decimal
from django.contrib.auth import get_user_model
from inventory.exceptions import UpdateOrDeleteIsForbidden
from rest_framework.exceptions import APIException #pyright: ignore

User = get_user_model()

@pytest.fixture
def api_rf():
    """Provides an APIRequestFactory instance for serializer context."""
    return APIRequestFactory()

@pytest.fixture
def clerk_user(db):
    """User WITHOUT supervisor permissions"""
    return User.objects.create_user(username="clerk", is_active=True)


@pytest.fixture
def serializer_context(api_rf, clerk_user):
    """Provides standard serializer context with a mock request and authenticated user."""
    request = api_rf.post('/')
    request.user = clerk_user
    return {'request': request}


@pytest.mark.django_db
class TestMovementSerializer:

    @pytest.fixture
    def measure_unit_item(self):
        return MeasureUnit.objects.create(
            name = 'mock',
            symbol = 'mk',
            is_decimal = True,
        )

    @pytest.fixture
    def masterdata_item(self, measure_unit_item):
        """Creates a sample Masterdata instance"""
        return Inv_masterdata.objects.create(
            sku = 'MOCK24',
            barcode = '978020137962',
            desc = 'mocker',
            measureUnit = measure_unit_item,
            price = 9.99,
        )
    
    @pytest.fixture
    def inventory_item(self, masterdata_item):
        """Creates a sample Inventory instance."""
        return Inventory.objects.create(
            quantity = 5,
            inv_masterdata = masterdata_item,
        )

    @pytest.fixture
    def movement_instance(self, inventory_item):
        """Creates a sample Movement instance for testing update restrictions."""
        return Movement.objects.create(
            inventory_id=inventory_item,
            operation_direction="IN",
            quantity=10,
        )

    # ------------------------------------------------------------------
    # POST / Create Tests
    # ------------------------------------------------------------------

    @patch('inventory.serializers.InventoryOrchestrator.validate_movement_create')
    def test_movement_create_validation_success(
        self, mock_orchestrator, inventory_item, serializer_context
    ):
        """Test successful deserialization and orchestrator call during creation."""
        payload = {
            "inventory_id": inventory_item.id,
            "operation_direction": "IN",
            "quantity": 10,
            "correction_id": None,
            "created_by": None,
        }

        serializer = MovementSerializer(data=payload, context=serializer_context)

        assert serializer.is_valid(), serializer.errors
        
        # Verify InventoryOrchestrator.validate_movement_create was called once
        assert mock_orchestrator.call_count == 1
        
        # Verify passed arguments to the orchestrator
        call_args, call_kwargs = mock_orchestrator.call_args
        assert call_args[0] == inventory_item  # inventory_item
        assert isinstance(call_args[1], Movement)  # movement_item
        movement_item = call_args[1]
        assert Decimal(movement_item.quantity) == 10    #test arguments were passed correctly to the orchestrator
        assert call_kwargs['user'] == serializer_context['request'].user

    @patch('inventory.serializers.InventoryOrchestrator.validate_movement_create')
    def test_movement_create_invalid_inventory_id(
        self, mock_orchestrator, serializer_context
    ):
        """Test failure when referenced inventory_id does not exist."""
        payload = {
            "inventory_id": 999999,  # Non-existent ID
            "operation_direction": "IN",
            "quantity": 5,
        }

        serializer = MovementSerializer(data=payload, context=serializer_context)

        assert not serializer.is_valid()
        assert "inventory_id" in serializer.errors
        mock_orchestrator.assert_not_called()

    # ------------------------------------------------------------------
    # PUT / PATCH / Update Tests
    # ------------------------------------------------------------------

    def test_movement_update_forbidden(
        self, movement_instance, serializer_context
    ):
        """Test that updating an existing Movement raises UpdateOrDeleteIsForbidden."""
        payload = {
            "inventory_id": movement_instance.inventory_id.id,
            "operation_direction": "OUT",
            "quantity": 20,
        }

        serializer = MovementSerializer(
            instance=movement_instance,
            data=payload,
            partial=True,
            context=serializer_context,
        )

        assert not serializer.is_valid()

    # ------------------------------------------------------------------
    # Serialization / Output Tests
    # ------------------------------------------------------------------

    def test_movement_serialization_fields(self, movement_instance, serializer_context):
        """Test that serializer outputs all required fields properly."""
        serializer = MovementSerializer(movement_instance, context=serializer_context)
        data = serializer.data

        assert data["id"] == movement_instance.id
        assert data["inventory_id"] == movement_instance.inventory_id.id
        assert data["operation_direction"] == "IN"
        assert Decimal(data["quantity"]) == 10
        assert "correction_id" in data
        assert "created_by" in data