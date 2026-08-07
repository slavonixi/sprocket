from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from rest_framework import serializers # pyright: ignore[reportMissingImports, reportMissingModuleSource]

######################
# Models importations
######################
from inventory.models import Inventory
from inventory.models import Inv_masterdata
from inventory.models import MeasureUnit


########## MeasureUnitSerializer ######
## ##
#######################################

class MeasureUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasureUnit
        fields = [
            "url",
            "id",
            "name",
            "symbol",
            "is_decimal",
        ]

########## MovementSerializer #########
## ##
#######################################


class MovementSerializer(serializers.HyperlinkedModelSerializer):

    inventory_id = serializers.HyperlinkedRelatedField(
        queryset = Inventory.objects.all(),    
        view_name='inventory-detail',  
    )
    class Meta:
        model = MeasureUnit
        fields = [
            "url",
            "id",
            "inventory_id",
            "quantity",
        ]

########## Inv_masterdataSerializer ###
## ##
#######################################

class Inv_masterdataSerializer(serializers.HyperlinkedModelSerializer):
    
    measureUnit = serializers.PrimaryKeyRelatedField(
        queryset = MeasureUnit.objects.all()
    )
    
    class Meta:
        model = Inv_masterdata
        fields = [
            "url",
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

class InventorySerializerList(serializers.HyperlinkedModelSerializer):
    
    measureUnit = serializers.SerializerMethodField(read_only=True)

    inv_masterdata = serializers.HyperlinkedRelatedField(
        queryset = Inv_masterdata.objects.all(),    
        view_name='inv_masterdata-detail', # Deve corrispondere al nome nel router    
    )

    desc = serializers.CharField(source="inv_masterdata.desc", read_only = True)


    class Meta: 
        model = Inventory
        fields = [
            "url",
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

class InventorySerializerDetail(serializers.HyperlinkedModelSerializer):
    inv_masterdata = serializers.HyperlinkedRelatedField(
        queryset = Inv_masterdata.objects.all(),    
        view_name='inv_masterdata-detail', # Deve corrispondere al nome nel router    
    )    
    class Meta:
        model = Inventory
        fields = [
            'url',
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
