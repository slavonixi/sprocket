from report import models
from report import permissions
from report.services.report_orchestrator import ReportOrchestrator
from rest_framework import generics
from django.contrib.auth.models import User
from report.serializers import (
    ReportSerializer,
    ReportSerializerDetail,
    ReportAndOperationCreateSerializer,
    OperationSerializer,
    UsedMaterialsSerializer,
)

from core.permissions import IsOwnerOrReadOnly

from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status


class UsedMaterialsViewSet(viewsets.ModelViewSet):

    serializer_class = UsedMaterialsSerializer
    queryset = models.UsedMaterials.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        qty_requested = serializer.validated_data['qta']
        inventory_id = serializer.validated_data['inventory_fk'].id
        operation_obj = serializer.validated_data['operation_fk']
        #ServiceOrchestrator.withdraw_inventory(inventory_id, qty_requested) #orchestrator
        serializer.save()

    def perform_update(self, serializer):
        inventory_id = serializer.validated_data['inventory_fk'].id
        old_quantity = self.get_object().qta
        new_quantity = serializer.validated_data.get('qta')

        #ServiceOrchestrator.update_withdraw(inventory_id, old_quantity, new_quantity) #orchestrator
        serializer.save()

    def perform_delete(self, instance):
        quantity_to_restore = instance.qta
        inventory_id = instance.inventory.fk.id
        #ServiceOrchestrator.delete_withdraw(quantity_to_restore)
        instance.delete()



class OperationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    # def get_serializer_class(self):
    #      if self.action == 'list':
    #         return OperationSerializerList
    #      return OperationSerializerDetail

    queryset = models.Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated]

    ########################################
    ######      OPERATION PLAN        ######
    ########################################

    @action(
          detail=False,
          methods=['post'],
          permission_classes=[permissions.CanPlanOperation]
    )
    def plan(self, request, pk=None):
        """
        Route: POST /api/v1/operation/plan/
        Plan an operation
        """
        # serializer and field validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        ReportOrchestrator.add_operation(
            request.user,
            validated_data,
            is_planning=True,
        )

        return Response
            {"detail": _("operation created")},
            status=status.HTTP_201_CREATED
        )

    ########################################
    ######   OPERATION QUICKSTART     ######
    ########################################

    @action(
          detail=False,
          methods=['post'],
          permission_classes=[permissions.CanStartOperation]
    )
    def quickstart(self, request, pk=None):
        """
        Route: POST /api/v1/operation/quickstart/
        quickstart an operation
        """
        # serializer and field validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        ReportOrchestrator.add_operation(
            request.user,
            validated_data,
            is_planning=False,
        )

        return Response
            {"detail": _("operation has been created and started")},
            status=status.HTTP_201_CREATED
        )


class ReportViewSet(viewsets.ModelViewSet):
    """
        Provide Report information
    """

    # Differenziare 2 endpoint per 'planning' e 'starting'

    def get_serializer_class(self):
        if self.action == 'create':
            # Giving the possibility to create the operation in the same moment
            return ReportAndOperationCreateSerializer
        else:
            # should add the check for details or list (information are very different)
            return ReportSerializer

    queryset = models.Report.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    ########################################
    ######        REPORT PLAN         ######
    ########################################

    @action(
          detail=False,
          methods=['post'],
          permission_classes=[permissions.CanPlanReport]
    )
    def plan(self, request, pk=None):
        """
        Route: POST /api/v1/report/plan/
        Plan a report
        """
        # serializer and field validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data.get('operation'):
            # if operation is provided in the request
            # create both contestually
            ReportOrchestrator.create_report_and_operation(
                request.user,
                validated_data,
                is_planning=True,
            )
        else:
            # otherwise create only the empty report
            ReportOrchestrator.create_empty_report(
                request.user,
                validated_data
            )
        return Response(
            {"detail": _("report created")},
            status=status.HTTP_201_CREATED
        )

    ########################################
    ######       REPORT START         ######
    ########################################

    @action(
          detail=False,
          methods=['post'],
          permission_classes=[permissions.CanStartReport]
    )
    def quickstart(self, request, pk=None):
        """
        Route: POST /api/v1/report/quickstart/
        quickstart a report
        """
        # serializer and field validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data.get('operation'):
            # operation must be included in the payload
            # during a quickstart
            ReportOrchestrator.create_report_and_operation(
                request.user,
                validated_data,
                is_planning=False,
            )
        else:
            return Response(
                {"detail": "provide operation data in order to quickstart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Report quickstart has been successful"},
            status=status.HTTP_201_CREATED
        )


    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            method="POST",
            detail="La creazione diretta non è consentita. Utilizza /operations/plan/ o /operations/start/."
        )
