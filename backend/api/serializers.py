from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from rest_framework import serializers # pyright: ignore[reportMissingImports, reportMissingModuleSource]
from .inventory_services import InventoryServices

#   MODELS
from .models import Report
from .models import HR_records
from .models import Customer_records
from .models import Operation
from .models import Inventory
from .models import Inv_masterdata
from .models import MeasureUnit
from .models import Machinery_records
from .models import UsedMaterials
from .models import Logs

class LogsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Logs
        fields = [
            "url",
            "id",
            "log_text",
        ]

class UsedMaterialsSerializer(serializers.HyperlinkedModelSerializer):
    
    operation_fk = serializers.HyperlinkedRelatedField(
        queryset = Operation.objects.all(),    
        view_name='operation-detail', # Deve corrispondere al nome nel router    
    )
    inventory_fk = serializers.HyperlinkedRelatedField(
        queryset = Inventory.objects.all(),    
        view_name='inventory-detail', # Deve corrispondere al nome nel router    
    )
    desc = serializers.CharField(source="inventory_fk.inv_masterdata.desc", read_only = True)


    class Meta:
        model = UsedMaterials
        fields = [
            "url",
            "id",
            "operation_fk",
            "inventory_fk",
            "desc",
            "qta",
        ]

    def validate(self, data):
        if self.instance:
            # Siamo in un UPDATE (PUT/PATCH)
            # Posso confrontare data.get('quantity') con self.instance.quantity
            old_qta = self.instance.qta
            new_qta = data.get('qta')
            inventory_item = data.get('inventory_fk')
            InventoryServices.validate_stock_update(inventory_item, old_qta, new_qta)     

        else:
            # Siamo in un CREATE (POST)
            inventory_item = data.get('inventory_fk')
            qta = data.get('qta')
            InventoryServices.validate_stock_reduction(inventory_item, qta)        
        return data
     
class Machinery_recordsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Machinery_records
        fields = [
            "url",
            "id",
            "brand",
            "model",
        ]    

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
     
# """
# ****************************************************************************************
#     |----OPERATION SERIALIZER DETAIL-----|

#     An operation is a step of a report: it may be compose by 1 or even 100 operations.

#     In OperationSerializer"Detail" every information and hypertext is provided

#         #To add details | list ?
# """
class OperationSerializerDetail(serializers.HyperlinkedModelSerializer):

    report_fk = serializers.HyperlinkedRelatedField(
        queryset = Report.objects.all(),    
        view_name='report-detail', # Deve corrispondere al nome nel router    
    )

    technician_fk = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='hr_records-detail', # Deve corrispondere al nome nel router
        queryset=HR_records.objects.all(),
    )

    involved_materials = serializers.HyperlinkedRelatedField(
        source='involved_materials_queryset', # HR_records method which provide technician urls
        many=True,
        read_only=True,
        view_name='inventory-detail',
    )
        

    class Meta:
        model = Operation
        fields = [
            "url",
            "id", 
            "date",
            "desc",
            "report_fk",
            "technician_fk",
            "involved_materials",
        ]
        
# """
# ****************************************************************************************
#     |----OPERATION SERIALIZER ***LIST***-----|

    
#         (not return only technicians)
# """
class OperationSerializerList(serializers.HyperlinkedModelSerializer):
    report_fk = serializers.HyperlinkedRelatedField(
        queryset = Report.objects.all(),    
        view_name='report-detail', # Deve corrispondere al nome nel router    
    )

    class Meta:
        model = Operation
        fields = [
            "url",
            "id", 
            "date",
            "desc",
            "report_fk",
        ]

# """
# ****************************************************************************************
#     |----CUSTOMER RECORDS SERIALIZER-----|
#     Just serialize customers (models.Customer_records)
# """
class Customer_recordsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Customer_records
        fields = [
            "url",
            "id", 
            "iva",
            "desc",
        ]

# """
# ****************************************************************************************
#     |----HR_RECORDS SERIALIZER-----|
#     Just serialize HR (models.HR_records)
# """
class HR_recordsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = HR_records
        fields = [
            "url",
            "name",
            "surname",
            "date_birth",
        ]

# """
# ****************************************************************************************
    # |----REPORT SERIALIZER LIST-----|
    # This serializer provide to return a list of reports with essential
    # information
# 
    # Many fields are missing for avoid to overflow the payload
# 
    # More details are provided in ReportSerializerDetail 
# """

class ReportSerializerList(serializers.HyperlinkedModelSerializer):

    customer_fk = serializers.HyperlinkedRelatedField(
        view_name = "customer_records-detail",
        read_only = True,
    )

    class Meta:
        model = Report
        fields = [
            "url",
            "report_id",
            "desc",
            "customer_fk",
            "date_open",
            "date_close",
            "status",
        ]

# 
# ****************************************************************************************
#     |----REPORT SERIALIZER DETAIL-----|

#     is used when an action different from "get list" is sent.

#     It adds the following information:
#         -involved operations (read only - its not a field)
#         -involved technicians (read only - its not a field)
#         - ***ANY OTHER FIELDS WILL BE DEPLOY*** 


    
# 
class ReportSerializerDetail(serializers.HyperlinkedModelSerializer):
#    
#    owner = serializers.ReadOnlyField(source="owner.username")
#        eventually develop a technician who owns a report (r u d)
#
#        any other involved technician will be only able to read n update (?)
    


    customer_fk = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='customer_records-detail', 
        queryset=Customer_records.objects.all(),
    )

    involved_operations = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='operation-detail',
        source='operation_set',        # Reverse relation*:
    )
    # """
    #        *report_fk is an operation's field: with source="operation_set"
    #        we're putting involved operation's report_fk in report ViewSet
    # """

    involved_technicians = serializers.HyperlinkedRelatedField(
        source='involved_technicians_queryset', # HR_records method which provide technician urls
        many=True,
        read_only=True,
        view_name='hr_records-detail'
    )

    class Meta:
        model = Report
        fields = [
            "url",
            "report_id",            #UUID*
            "desc",
            "date_open",
            "date_close",
            "involved_technicians", #every technicians's url who perform any operation*
            "involved_operations",  #every operation's url related to a report*
            "customer_fk",          #just the customer*
            "status",
        ]



