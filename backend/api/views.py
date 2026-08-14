from . import serializers, models
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import ReportSerializerList
from .serializers import ReportSerializerDetail
from .serializers import HR_recordsSerializer
from .serializers import Customer_recordsSerializer
from .serializers import OperationSerializerList
from .serializers import OperationSerializerDetail
from .serializers import Machinery_recordsSerializer
from .serializers import UsedMaterialsSerializer
from .serializers import LogsSerializer

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

from inventory.services import inventory_orchestrator

@api_view(['POST'])
@permission_classes([permissions.AllowAny]) # In produzione usa IsAuthenticated
def receive_log(request):
    """
    Endpoint che riceve un messaggio via POST e lo salva nel DB.
    """
    # 1. Recuperiamo il testo dalla richiesta HTTP
    message = request.data.get('log_text')
    models.Logs.objects.create(message)

    if not message:
        return Response({"error": "Nessun testo fornito"}, status=status.HTTP_400_)


class LogsViewSet(viewsets.ModelViewSet):

    serializer_class = LogsSerializer
    queryset = models.Logs.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
class Machinery_recordsViewSet(viewsets.ModelViewSet):

    serializer_class = Machinery_recordsSerializer
    queryset = models.Machinery_records.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    

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
    
    def get_serializer_class(self):
         if self.action == 'list':
            return OperationSerializerList
         return OperationSerializerDetail
    
    queryset = models.Operation.objects.all()
    #serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated]

class HR_recordsViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = models.HR_records.objects.all()
    serializer_class = HR_recordsSerializer
    permission_classes = [permissions.IsAuthenticated]

class Customer_recordsViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    queryset = models.Customer_records.objects.all()
    serializer_class = Customer_recordsSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    def get_serializer_class(self):
         if self.action == 'list':
            return ReportSerializerList
         return ReportSerializerDetail

    queryset = models.Report.objects.all()
    #serializer_class = ReportSerializerList
    permission_classes = [permissions.IsAuthenticated]


"""
class SnippetViewSet(viewsets.ModelViewSet):
    ""
    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    ""

    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=request.user)
"""