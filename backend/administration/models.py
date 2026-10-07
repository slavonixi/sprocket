from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
from inventory.models import Movement
from inventory.models import Inventory
# """
# #                   **************************************************************
# #   EAN13Field is a custom Field for EAN13 standard barcode.
# #   It performs some check-up and, eventually, throws an error message
# #
# """

# """
# #                   **************************************************************
# #   MeasureUnit is a table that contains all standards measure unit
# #
# #
# """


#                   **************************************************************
#   Customer_record is the list that contains every client
#
#
class Customer_records(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="ID univoco generato automaticamente (UUID4)"
    )
    iva = models.CharField(
        max_length=11,
        default = None,
        null = True,
        blank = True,
    )
    desc = models.CharField(max_length=100)

    def __str__(self):
        return self.desc
    
#                   **************************************************************
#   HR_records contains the human resources of the company.
#
#
class HR_records(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    date_birth = models.DateField()
    def __str__(self):
        return f"{self.name} {self.surname}"

#                   **************************************************************
#   A Report is a formal way to define an intervent, it contains:
#       -every operation (spread in many days)
#       -every material used and it prize
#       -Tecnicians and labor costs
#       -The machineries in matter
#


#                   **************************************************************
#   Machinery_records contains every machinery 
#   to which manuteneur is carried out by the company
#
class Machinery_records(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=100)


########## UserMaterials ##############
## To move in "operation" django app ##
#######################################


class Logs(models.Model):
    
    log_text = models.TextField()

   # id_masterdata (PK): Identificatore univoco (UUID o Int).
   # • sku: Codice alfanumerico per identificazione rapida (es. "CPU-INT-I7").
   # • barcode: Codice a barre (EAN13, UPC).
   # • desc: Nome esteso dell'articolo.
   # • id_category (FK): Collegamento alla tabella categorie.
   # • measure: Unità base (pz, kg, m).
   # • price: Valore monetario indicativo.
   # • weight: Dati logistici per calcolo spedizioni.