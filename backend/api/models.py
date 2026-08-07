from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
import inventory
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
    iva = models.CharField(max_length=11)
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
class Report(models.Model):
    class Report_status(models.TextChoices):
        DRAFT = "DR", _("Draft")
        OPEN = "OP", _("Open")
        CLOSED = "CL", _("Closed")     

    report_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="ID univoco generato automaticamente (UUID4)"
    )
    desc = models.CharField(max_length=100)
    customer_fk = models.ForeignKey(Customer_records, on_delete=models.CASCADE)
    date_open = models.DateTimeField("date opened")
    date_close = models.DateTimeField("date closed")
    #technicians = models.ManyToManyField(HR_records)   #spostato in Operation
    status = models.CharField(
        max_length = 2,
        choices = Report_status,
        default = Report_status.DRAFT,
    )

    @property
    def involved_technicians_queryset(self):
        # Usiamo 'self' perché siamo dentro il modello
        return HR_records.objects.filter(operation__report_fk=self).distinct()
    
    def __str__(self):
        return self.desc

#                   **************************************************************
#   Operation contains every single operation that will appear in the 
#   report
#
class Operation(models.Model):
    date = models.DateTimeField("operation's date")
    desc = models.CharField(max_length=500)
    report_fk = models.ForeignKey(Report, on_delete=models.CASCADE)
    technician_fk = models.ManyToManyField(HR_records)

    @property
    def involved_materials_queryset(self):
        # Usiamo 'self' perché siamo dentro il modello
        return inventory.Inventory.objects.filter(usedmaterials__operation_fk=self).distinct()


    def __str__(self):
        return self.desc


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
class UsedMaterials(models.Model):

    operation_fk = models.ForeignKey(Operation, on_delete=models.PROTECT)
    inventory_fk = models.ForeignKey('inventory.Inventory', on_delete=models.PROTECT)
    qta = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       verbose_name=_("qta"),
    )


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