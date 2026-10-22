import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

#OTHER MODELS
from inventory.models import Movement
from inventory.models import Inventory
from administration.models import HR_records
from administration.models import (
    Customer_records,
    Machinery_records,
)

class Report(models.Model):
    # Identificatore univoco globale per sincronizzazione offline sicura (evita collisioni ID)
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Codice human-readable progressivo (es. REP-2026-0001) per la ricerca rapida in azienda
    code = models.CharField(max_length=50, unique=True, db_index=True)

    # Relazioni anagrafiche principali
    customer_fk = models.ForeignKey(Customer_records, on_delete=models.PROTECT, related_name='reports')
    machinery_fk = models.ForeignKey(Machinery_records, on_delete=models.PROTECT, related_name='reports', null=True, blank=True)

    # Classificazione e Priorità
    class Priority(models.TextChoices):
        LOW = 'LOW', _('LOW')
        MEDIUM = 'MED', _('MED')
        HIGH = 'HIGH', _('HIGH')
        EMERGENCY = 'EMG', _('EMG')

    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    class ReportStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PLANNED = 'PLANNED', _('Planned')
        OPEN = 'OPEN', _('OPEN')
        ON_HOLD = 'ON_HOLD', _('ON_HOLD')
        COMPLETED = 'COMPLETED', _('COMPLETED')
        CLOSED = 'CLOSED', _('CLOSED')
        CANCELLED = 'CANCELLED', _('CANCELLED')

    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.DRAFT)

    # Descrizioni e Note
    title = models.CharField(max_length=255) # Oggetto sintetico del guasto/intervento
    description = models.TextField(blank=True) # Descrizione dettagliata fornita dal cliente/admin
    internal_notes = models.TextField(blank=True, help_text="Note visibili solo agli amministratori/caporeparto")

    # Timestamp e Metadati temporali
    date_created = models.DateTimeField(auto_now_add=True)
    date_scheduled = models.DateTimeField(null=True, blank=True, help_text="Data stimata di intervento")
    date_started = models.DateTimeField(null=True, blank=True)
    date_closed = models.DateTimeField(null=True, blank=True)

    # Audit trail (Chi ha creato/modificato)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_reports')

    # Campi tecnici per la sincronizzazione offline (Conflict Resolution)
    synced_at = models.DateTimeField(null=True, blank=True, help_text="Ultimo timestamp di sincronizzazione mobile")
    device_local_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID generato dal device offline")

    def __str__(self):
        return self.desc

    class Meta:
        indexes = [
            models.Index(fields=['status', 'date_scheduled']),
            models.Index(fields=['customer_fk']),
        ]

        permissions = [
            ("can_draft_report", _("Can draft reports")),
        ]

    #############################
    #   REPORT LOGIC METHODS    #
    #############################


    def set_initial_status(self, operations : Boolean, publish_now : Boolean):
        """
            Set the status of the report taking into account:
                - if there are operations linked to it
                - if the report has to be published now or not
        """
        if self.status:
            # if the status was already set by a supervisor
            # let it be
            return False

        if publish_now:
            # Publish the report means that it IS NOT a 'DRAFT'
            if operations:
                # If there are operations the entire report is 'PLANNED'
                report_orm.status = Report.ReportStatus.PLANNED
            else:
                # If there aren't, the report is simply 'OPEN'
                report_orm.status = Report.ReportStatus.OPEN
        else:
            # Otherwise it is a 'DRAFT'
            report_orm.status = Report.ReportStatus.DRAFT


class Operation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relazione obbligatoria con il Report padre
    report_fk = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='operations')

    # Assegnazione Tecnici (Molti a Molti: un'operazione può essere fatta da più tecnici)
    technicians = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_operations', blank=True)

    class OperationStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PLANNED = 'PLANNED', _('Planned')
        RUNNING = 'RUNNING', _('Running')
        PAUSED = 'PAUSED', _('Paused')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    status = models.CharField(max_length=20, choices=OperationStatus.choices, default=OperationStatus.PLANNED)

    # Dettagli del task
    title = models.CharField(max_length=255) # Es. "Sostituzione cuscinetto asse principale"
    instructions = models.TextField(blank=True, help_text="Istruzioni operative assegnate dall'ufficio")
    work_notes = models.TextField(blank=True, help_text="Note tecniche inserite dal tecnico a fine intervento")

    # Tracciamento Temporale e Ore Lavorate
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    execution_start_date = models.DateTimeField(null=True, blank=True)
    execution_end_date = models.DateTimeField(null=True, blank=True)

    # Ore effettive spese (può essere inserito a mano o calcolato automaticamente dalle date)
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Campi di sincronizzazione offline
    synced_at = models.DateTimeField(null=True, blank=True)

    @property
    def involved_materials_queryset(self):
        return Inventory.objects.filter(usedmaterials__operation_fk=self).distinct()

    def __str__(self):
        return self.desc

    class Meta:
        ordering = ['scheduled_datetime']

        permissions = [
            ("can_plan_operations", _("Can assign technician or create draft operations")),
            ("can_run_operations", _("Can start an operation")),
        ]

    #############################
    #  OPERATION LOGIC METHODS  #
    #############################

    def set_initial_status(self, start_now : Boolean):
        if start_now:
            self.status = self.OperationStatus.RUNNING
        else:
            self.status = self.OperationStatus.PLANNED

class UsedMaterials(models.Model):

    operation_fk = models.ForeignKey(Operation, on_delete=models.PROTECT)
    inventory_fk = models.ForeignKey('inventory.Inventory', on_delete=models.PROTECT)
    qta = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       verbose_name=_("qta"),
    )
