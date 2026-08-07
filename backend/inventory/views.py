from django.shortcuts import render
from . import serializers, models
from rest_framework import generics
from django.contrib.auth.models import User

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


import inventory.models
import core.permissions

# Create your views here.
from .serializers import InventorySerializerList
from .serializers import InventorySerializerDetail
from .serializers import Inv_masterdataSerializer
from .serializers import MeasureUnitSerializer
from .serializers import MovementSerializer



class MeasureUnitViewSet(viewsets.ModelViewSet):

    serializer_class = MeasureUnitSerializer
    queryset = models.MeasureUnit.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    

class MasterdataViewSet(viewsets.ModelViewSet):

    serializer_class = Inv_masterdataSerializer
    queryset = models.Inv_masterdata.objects.all()
    permission_classes = [permissions.IsAuthenticated]

class MovementViewSet(viewsets.ModelViewSet):

    serializer_class = MovementSerializer
    queryset = models.Movement.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
class InventoryViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    
    def get_serializer_class(self):
         if self.action == 'list':
            return InventorySerializerList
         return InventorySerializerDetail
    
    queryset = models.Inventory.objects.all()
    permission_classes = [permissions.IsAuthenticated]
