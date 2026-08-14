from django.shortcuts import render
from . import serializers, models
from rest_framework import generics #pyright: ignore
from django.contrib.auth.models import User

from rest_framework import permissions #pyright: ignore
from rest_framework.decorators import api_view #pyright: ignore
from rest_framework.response import Response #pyright: ignore
from rest_framework.reverse import reverse #pyright: ignore
from rest_framework import renderers #pyright: ignore
from rest_framework import viewsets, mixins #pyright: ignore
from rest_framework.decorators import action #pyright: ignore
from rest_framework import status #pyright: ignore
from django.db import transaction 
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes #pyright: ignore
from rest_framework.response import Response #pyright: ignore
from rest_framework import permissions, status #pyright: ignore


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

class MovementViewSet(          #PUT, PATCH, DELETE are forbidden (http 405)
    mixins.CreateModelMixin,    # POST 
    mixins.ListModelMixin,      # GET list
    mixins.RetrieveModelMixin,  # GET detail
    viewsets.GenericViewSet
):

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
