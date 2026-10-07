from django.contrib.auth.models import User # pyright: ignore[reportMissingModuleSource]
from rest_framework import serializers # pyright: ignore[reportMissingImports, reportMissingModuleSource]

from inventory.services.inventory_services import InventoryServices
#from services.app_services import ServiceOrchestrator

#   MODELS
from report.models import Report
from administration.models import HR_records
from administration.models import Customer_records
from report.models import Operation
from report.models import UsedMaterials
from administration.models import Machinery_records

# EXTERNAL MODELS IMPORTATION (to delete)
from inventory.models import Inventory
from inventory.models import MeasureUnit
from inventory.models import Inv_masterdata
from inventory.models import Movement

class UsedMaterialsSerializer(serializers.ModelSerializer):
    
    operation_fk = serializers.HyperlinkedRelatedField(
        queryset = Operation.objects.all(),    
        view_name='api:operation-detail', # Deve corrispondere al nome nel router    
    )
    inventory_fk = serializers.HyperlinkedRelatedField(
        queryset = Inventory.objects.all(),    
        view_name='inventory:inventory-detail', # Deve corrispondere al nome nel router    
    )
    desc = serializers.CharField(source="inventory_fk.inv_masterdata.desc", read_only = True)


    class Meta:
        model = UsedMaterials
        fields = [
            "id",
            "operation_fk",
            "inventory_fk",
            "desc",
            "qta",
        ]
        extra_kwargs = {
            'url': {'view_name': 'api:usedmaterials-detail'}
        }



    def validate(self, data):
        if self.instance:
            # Siamo in un UPDATE (PUT/PATCH)
            # Posso confrontare data.get('quantity') con self.instance.quantity
            old_qta = self.instance.qta
            new_qta = data.get('qta')
            inventory_item = data.get('inventory_fk')
            #ServiceOrchestrator.validate_withdraw_update(inventory_item, old_qta, new_qta)     

        else:
            # Siamo in un CREATE (POST)
            inventory_item = data.get('inventory_fk')
            qta = data.get('qta')
            
            #ServiceOrchestrator.validate_inventory_withdraw(inventory_item, qta)        
        return data

class OperationSerializerDetail(serializers.ModelSerializer):

    report_fk = serializers.HyperlinkedRelatedField(
        queryset = Report.objects.all(),    
        view_name='api:report-detail', # Deve corrispondere al nome nel router    
    )

    technician_fk = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='api:hr_records-detail', # Deve corrispondere al nome nel router
        queryset=HR_records.objects.all(),
    )

    involved_materials = serializers.HyperlinkedRelatedField(
        source='involved_materials_queryset', # HR_records method which provide technician urls
        many=True,
        read_only=True,
        view_name='inventory:inventory-detail',
    )
        

    class Meta:
        model = Operation
        fields = [
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
class OperationSerializerList(serializers.ModelSerializer):
    report_fk = serializers.HyperlinkedRelatedField(
        queryset = Report.objects.all(),    
        view_name='api:report-detail', # Deve corrispondere al nome nel router    
    )

    class Meta:
        model = Operation
        fields = [
            "id", 
            "date",
            "desc",
            "report_fk",
        ]

class ReportSerializerList(serializers.ModelSerializer):

    customer_fk = serializers.HyperlinkedRelatedField(
        view_name = "api:customer_records-detail",
        read_only = True,
    )

    class Meta:
        model = Report
        fields = [
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
class ReportSerializerDetail(serializers.ModelSerializer):
#    
#    owner = serializers.ReadOnlyField(source="owner.username")
#        eventually develop a technician who owns a report (r u d)
#
#        any other involved technician will be only able to read n update (?)
    

    customer_fk = serializers.HyperlinkedRelatedField(
        many=False,
        view_name='api:customer_records-detail', 
        queryset=Customer_records.objects.all(),
    )

    involved_operations = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='api:operation-detail',
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
        view_name='administration:hr_records-detail'
    )

    class Meta:
        model = Report
        fields = [
            "report_id",            #UUID*
            "desc",
            "date_open",
            "date_close",
            "involved_technicians", #every technicians's url who perform any operation*
            "involved_operations",  #every operation's url related to a report*
            "customer_fk",          #just the customer*
            "status",
        ]

    def validate(self, data):
        if self.instance:
            pass
        else:       #REPORT CREATION (POST)
            request = self.context.get('request')
            user = request.user if request else None
            report_item = Report(**data)
            ReportOrchestrator.validate_report_creation(report_item)
            return data