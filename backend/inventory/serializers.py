from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from rest_framework import serializers # pyright: ignore[reportMissingImports, reportMissingModuleSource]

#######################
# Models importations #
#######################
from inventory.models import Inventory
from inventory.models import Inv_masterdata
from inventory.models import MeasureUnit
from inventory.models import Movement

#########################
# Services importations #
#########################
from inventory.services.movement_services import MovementServices
from inventory.services.inventory_services import InventoryServices
from inventory.services.inventory_orchestrator import InventoryOrchestrator


########## MeasureUnitSerializer ######

#######################################

class MeasureUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureUnit
        fields = [
            "id",
            "name",
            "symbol",
            "is_decimal",
        ]

########## MovementSerializer #########
## ##
#######################################


class MovementSerializer(serializers.ModelSerializer):

    inventory_id = serializers.HyperlinkedRelatedField(
        queryset = Inventory.objects.all(),    
        view_name='inventory-detail',  
    )
    class Meta:
        model = MeasureUnit
        fields = [
            "id",
            "inventory_id",
            "quantity",
        ]

    def validate(self, data):
        if self.instance:   #PUT/PATCH (update)
            new_qty = data.qty
            InventoryOrchestrator.validate_movement_update(
                self.instance.inventory_id, 
                self.instance,
                new_qty
            )
        else:               #POST (create)
            movement_item = Movement(
                data.id,
                data.inventory_id,
                data.qty,
            )
            InventoryOrchestrator.validate_movement_create(
                movement_item.inventory_id,
                movement_item,
            )
                 
########## Inv_masterdataSerializer ###
## ##
#######################################

class Inv_masterdataSerializer(serializers.ModelSerializer):
    
    measureUnit = serializers.PrimaryKeyRelatedField(
        queryset = MeasureUnit.objects.all()
    )
    
    class Meta:
        model = Inv_masterdata
        fields = [
            "sku",
            "barcode",
            "desc",
            "measureUnit",
            "price",
            "measure_value",   
        ]

########## InventorySerializerList ####
## ##
#######################################

class InventorySerializerList(serializers.ModelSerializer):
    
    measureUnit = serializers.SerializerMethodField(read_only=True)

    inv_masterdata = serializers.HyperlinkedRelatedField(
        queryset = Inv_masterdata.objects.all(),    
        view_name='inv_masterdata-detail', # Deve corrispondere al nome nel router    
    )

    desc = serializers.CharField(source="inv_masterdata.desc", read_only = True)


    class Meta: 
        model = Inventory
        fields = [
            "id",
            "inv_masterdata",
            "desc",
#            "desc",
#            "qta", #measure + unit
            #write only
            "quantity",
            "measureUnit",
        ]

    def get_measureUnit(self, obj):
        
        # [1] Il campo nel modello si chiama 'measure'
        unit = obj.inv_masterdata.measureUnit.symbol
        return unit
    

    
########## InventorySerializerDetail ##
## ##
#######################################

class InventorySerializerDetail(serializers.ModelSerializer):
    inv_masterdata = serializers.HyperlinkedRelatedField(
        queryset = Inv_masterdata.objects.all(),    
        view_name='inv_masterdata-detail', # Deve corrispondere al nome nel router    
    )    
    class Meta:
        model = Inventory
        fields = [
            'id',
            'inv_masterdata',
            'quantity',
        ]

    def validate(self, data):
        inv_masterdata = data.get('inv_masterdata')
        quantity = data.get('quantity')
        inventory_item = Inventory(
                                    inv_masterdata=inv_masterdata, 
                                    quantity=quantity                                    
                                    )
        InventoryServices.validate_item(inventory_item)
        return data
     
########## MovementSerializer ###
## ##
#######################################
