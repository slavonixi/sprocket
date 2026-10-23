import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

#OTHER MODELS
from inventory.models import Movement
from inventory.models import Inventory
from administration.models import (
    Customer_records,
    Machinery_records,
    HR_records,
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
            ("can_override_report", _("Can override reports")),
            ("can_plan_report", _("Can plan reports")),
            ("can_start_report", _("Can start reports")),
        ]

    #############################
    #   REPORT LOGIC METHODS    #
    #############################

    @property
    def is_open_for_operations(self):
        if self.status not in [
            self.ReportStatus.COMPLETED,
            self.ReportStatus.CLOSED,
            self.ReportStatus.CANCELLED
        ]:
            return True
        else:
            return False

    def calculate_initial_status(self, *, publish_now=False, has_operations=False, is_planned=False):
        calc_status = None
        if self.status:
            # if the status is already set, the user is a supervisor
            return self.status
        else:
            # is the report being published?
            if publish_now:
                # if the report has to be published check if there are planned operations
                if has_operations and is_planned:
                    # if yes, the report is planned
                    calc_status = self.ReportStatus.PLANNED
                else:
                    # otherwise the operations are drafts and the report is simply open
                    calc_status = self.ReportStatus.OPEN
            else:
                # if the report is not being published, it is a DRAFT
                calc_status = self.ReportStatus.DRAFT

        return calc_status

class Operation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relazione obbligatoria con il Report padre
    report_fk = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='operations')

    # Assegnazione Tecnici (Molti a Molti: un'operazione può essere fatta da più tecnici)
    technicians = models.ManyToManyField(HR_records, related_name='assigned_operations', blank=True)

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

    @property
    def is_planned(self):
        return self.status == self.OperationStatus.PLANNED

    def __str__(self):
        return self.desc

    class Meta:
        ordering = ['scheduled_datetime']

        permissions = [
            ("can_override_operation", _("Can override an operation")),
            ("can_plan_operation", _("Can plan an operation")),
            ("can_start_operation", _("Can start an operation")),
        ]

    #############################
    #  OPERATION LOGIC METHODS  #
    #############################

    def calculate_initial_status(self, start_now : bool, has_technicians : bool):
        calc_status = None
        if start_now:
            if has_technicians:
                calc_status = self.OperationStatus.RUNNING
        else:
            if has_technicians and self.scheduled_datetime:
                calc_status = self.OperationStatus.PLANNED
            else:
                calc_status = self.OperationStatus.DRAFT


        return calc_status

class UsedMaterials(models.Model):

    operation_fk = models.ForeignKey(Operation, on_delete=models.PROTECT)
    inventory_fk = models.ForeignKey('inventory.Inventory', on_delete=models.PROTECT)
    qta = models.DecimalField(
       max_digits=10,
       decimal_places=2,
       verbose_name=_("qta"),
    )
