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
#########################################


class Machinery_recordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machinery_records
        fields = [
            "id",
            "brand",
            "model",
        ]       
        # extra_kwargs = {
        #     'url': {'view_name': 'api:machinery_records-detail'}
        # }

# """
# ****************************************************************************************
#     |----OPERATION SERIALIZER DETAIL-----|

#     An operation is a step of a report: it may be compose by 1 or even 100 operations.

#     In OperationSerializer"Detail" every information and hypertext is provided

#         #To add details | list ?
# """

# """
# ****************************************************************************************
#     |----CUSTOMER RECORDS SERIALIZER-----|
#     Just serialize customers (models.Customer_records)
# """
class Customer_recordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer_records
        fields = [
            "id", 
            "iva",
            "desc",
        ]

# """
# ****************************************************************************************
#     |----HR_RECORDS SERIALIZER-----|
#     Just serialize HR (models.HR_records)
# """
class HR_recordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = HR_records
        fields = [
            "name",
            "surname",
            "date_birth",
        ]
            # extra_kwargs = {
            #     'url': {'view_name': 'api:hr_records-detail'}
            # }


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

