import pytest
from decimal import Decimal
from inventory.models import MeasureUnit, Inv_masterdata, Inventory, Movement
from inventory.services.inventory_orchestrator import InventoryOrchestrator


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