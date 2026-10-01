import pytest
from decimal import Decimal
from inventory.models import MeasureUnit, Inv_masterdata, Inventory, Movement
from inventory.services.inventory_orchestrator import InventoryOrchestrator
from inventory import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


#########################
##      FIXTURES       ##
#########################


@pytest.fixture
def sample_inventory(db):
    """Creates a sample Inventory item with initial stock of 100.00 kg"""
    unit = MeasureUnit.objects.create(name="Kilogram", symbol="kg", is_decimal=True)
    masterdata = Inv_masterdata.objects.create(
        sku="SKU-TEST-01",
        barcode="1234567890123",
        desc="Test Product",
        measureUnit=unit,
        price=Decimal("15.00")
    )
    return Inventory.objects.create(
        inv_masterdata=masterdata, 
        quantity=Decimal("100.00")
    )

@pytest.fixture
def sample_movement(db, sample_inventory):
    """Creates a sample Movement item with direction = INBOUND and quantity = 10.00"""
    
    return Movement.objects.create(
        inventory_id = sample_inventory,
        quantity = Decimal("10.00"),
        operation_direction = "IN",
        correction_id = None
    )

@pytest.fixture
def sample_adjust_movement(db, sample_inventory, sample_movement):
    """Creates a sample adjust Movement item with direction = INBOUND and quantity = 9.00"""
    
    return Movement.objects.create(
        inventory_id = sample_inventory,
        quantity = Decimal("9.00"),
        operation_direction = "IN",
        correction_id = sample_movement
    )


User = get_user_model()

@pytest.fixture
def supervisor_user(db):
    """User WITH the 'can_adjust_movement' permission"""
    user = User.objects.create_user(username="supervisor", is_active=True)
    
    # Assign custom permission
    content_type = ContentType.objects.get_for_model(Movement)
    perm = Permission.objects.get(codename="can_adjust_movement", content_type=content_type)
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def clerk_user(db):
    """User WITHOUT supervisor permissions"""
    return User.objects.create_user(username="clerk", is_active=True)

#########################
## MOVEMENT VALIDATION ##
#########################


@pytest.mark.django_db
def test_correction_raises_cannot_adjust_for_regular_clerk(sample_inventory, sample_adjust_movement, clerk_user):
    with pytest.raises(exceptions.CannotAdjustMovement):
        InventoryOrchestrator.validate_movement_create(
            sample_inventory, 
            sample_adjust_movement, 
            user=clerk_user
        )


@pytest.mark.django_db
def test_correction_succeeds_for_supervisor_user(sample_inventory, sample_adjust_movement, supervisor_user):
    InventoryOrchestrator.validate_movement_create(
        sample_inventory, 
        sample_adjust_movement, 
        user=supervisor_user
    )


#########################
##  MOVEMENT CREATION  ##
#########################

@pytest.mark.django_db
def test_create_inbound_movement_increases_stock(sample_inventory):
    initial_stock = sample_inventory.quantity  # 100.00
    inbound_movement = Movement(
        inventory_id=sample_inventory,
        quantity=Decimal("50.00"),
        operation_direction=Movement.OperationDirection.INBOUND
    )

    InventoryOrchestrator.create_new_movement(sample_inventory, inbound_movement)

    # Reload inventory item fresh from database
    sample_inventory.refresh_from_db()
    
    # Assert stock quantity increased to 150.00
    assert sample_inventory.quantity == Decimal("150.00")
    
    # Assert movement was saved in database with an ID
    assert inbound_movement.id is not None

@pytest.mark.django_db
def test_create_outbound_movement_decreases_stock(sample_inventory):
    outbound_movement = Movement(
        inventory_id=sample_inventory,
        quantity=Decimal("30.00"),
        operation_direction=Movement.OperationDirection.OUTBOUND
    )
    InventoryOrchestrator.create_new_movement(sample_inventory, outbound_movement)
    sample_inventory.refresh_from_db()
    assert sample_inventory.quantity == Decimal("70.00")

@pytest.mark.django_db
def test_invalid_operation_direction_raises_exception(sample_inventory):
    # 1. ARRANGE
    invalid_movement = Movement(
        inventory_id=sample_inventory,
        quantity=Decimal("10.00"),
        operation_direction="INVALID_DIR"  # Invalid!
    )

    # 2. ACT & ASSERT
    # Verify that calling orchestrator raises IllegalOperationValue exception
    with pytest.raises(exceptions.IllegalOperationValue):
        InventoryOrchestrator.create_new_movement(sample_inventory, invalid_movement)