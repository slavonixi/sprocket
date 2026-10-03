from administration import models
from rest_framework import generics
from django.contrib.auth.models import User
from administration.serializers import HR_recordsSerializer
from administration.serializers import Customer_recordsSerializer
from administration.serializers import Machinery_recordsSerializer

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


    
class Machinery_recordsViewSet(viewsets.ModelViewSet):

    serializer_class = Machinery_recordsSerializer
    queryset = models.Machinery_records.objects.all()
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