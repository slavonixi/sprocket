from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
import datetime
from inventory.models import Movement
from inventory.models import Inventory
from administration.models import HR_records
from administration.models import Customer_records
from administration.models import Machinery_records


class Report(models.Model):
    class Report_status(models.TextChoices):
        """
            Report's status (v3)
        """
        # A report is open, but nobody is working on it
        # atm and the tasks are not completed yet
        OPEN = "OP", _("Open")
        # All the work is done. The administration 
        # closes the report and then creates the invoice
        CLOSED = "CL", _("Closed")     
        # A work can be cancelled, if it was created
        # for mistake or the client is no longer interested 
        CANCELLED = "CA", _("Cancelled")
        # Technicians already completed some tasks, but the 
        # work is suspended due to parts shortage for instance
        HOLD_ON = "HO", _("Hold on")
        # Technician has closed a report and admin has to
        # approve the closure or re-open it
        PENDING = "PE", _("Pending")


    report_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="ID univoco generato automaticamente (UUID4)"
    )
    desc = models.CharField(max_length=100)
    customer_fk = models.ForeignKey(Customer_records, on_delete=models.PROTECT)
    date_open = models.DateTimeField(
        _("date opened"),
        default = None,
        null = True,
        blank = True,
    )        
    date_close = models.DateTimeField(
        _("date closed"),
        default = None,
        null = True,
        blank = True,
    )
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
    class Operation_status(models.TextChoices):
        """
            Operation's status (v1)
        """
        # An admin is building a report. Only him can see it
        DRAFT = "DR", _("Draft")
        # The operation is planned and technicians are assigned
        PLANNED = "PL", ("Planned")
        # The operation is done
        FINISHED = "FI", ("Finished")
        # Technicians are working on the field
        RUNNING = "RU", ("Running")

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
