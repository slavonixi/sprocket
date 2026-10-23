from report import models
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

    @action(detail=False, methods=['post'])
    def plan(self, request, pk=None):
        """
        Route: POST /api/operations/plan/
        Crea una nuova operazione pianificata.
        """
        # serializer and field validation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if validated_data['operation']:

        else:


        return Response(
            {"detail": "Operazione creata e pianificata con successo."},
            status=status.HTTP_201_CREATED
        )

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(
            method="POST",
            detail="La creazione diretta non è consentita. Utilizza /operations/plan/ o /operations/start/."
        )
