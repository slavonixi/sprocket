from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
from inventory.models import Movement
from inventory.models import Inventory
from administration.models import HR_records
from administration.models import Customer_records
from administration.models import Machinery_records


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
        return Inventory.objects.filter(usedmaterials__operation_fk=self).distinct()


    def __str__(self):
        return self.desc

class UsedMaterials(models.Model):

    operation_fk = models.ForeignKey(Operation, on_delete=models.PROTECT)
    inventory_fk = models.ForeignKey('inventory.Inventory', on_delete=models.PROTECT)
    qta = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       verbose_name=_("qta"),
    )
