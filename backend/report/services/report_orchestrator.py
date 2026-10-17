# SERVICES
from report.services.operation_services import OperationServices
from report.services.report_services import ReportServices
from django.utils.translation import gettext_lazy as _
from django.db import transaction


# MODELS
from report.models import (
    Report,
    Operation,
)

# EXCEPTIONS
from core.exceptions import BusinessLogicError

class ReportOrchestrator:

    SUPERVISOR_ONLY_FIELDS = (
        'status',
        'date_started',
        'date_closed',
    )

    #########################################
    #            Utils Methods              #
    #########################################

    @classmethod
    def get_instance(cls, report_data):
        report_data.pop('publish_immediately', None)
        report_data.pop('operation', None)
        return Report(**report_data)

    #########################################
    #    Permissions Validation Methods     #
    #########################################

    @classmethod
    def is_user_authenticated(cls, user):
        if not user or not user.is_authenticated:
            raise BusinessLogicError(
                _("You must be authenticated")
            )

    @classmethod
    def check_override_permissions(cls, user, report_data):
        """
            Is user trying to do an operations which require supervisor's permissions?
        """
        # check if user has supervisor's perms
        is_supervisor = user.has_perm('report.can_override_report')

        # Which protected fields did the user insert?
        protected_fields = [
            field for field in cls.SUPERVISOR_ONLY_FIELDS
            if field in validated_data
        ]

        if protected_fields and not is_supervisor:
            raise BusinessLogicError(
                _("You can't insert that fields")
            )

    @classmethod
    def check_planning_permissions(cls, user, report_data):
        """
            If the user is not an admin the publish_immediately flag
            is forced to True (for technicians).
            If you are an admin but the client didnt sent the flag
            a default (False) is set.
        """
        # check if the user can plan reports
        is_admin = user.has_perm('report.can_plan_report')

        if not is_admin:
            # If the user has not the permission to plan
            # must publish the report (technician)
            report_data['publish_immediately'] = True
        else:
            # If the user have perms but DID NOT sent the flag
            # we set a secure default (False, drafted)
            report_data.setdefault('publish_immediately', False)

    #########################################
    #          Validation Methods           #
    #########################################

    @classmethod
    def validate_create_report(cls, user, report_data):
        operation_data = report_data.get('operation') or {}
        # check if the creation is being managed by a supervisor
        cls.check_override_permissions(user, report_data):
        # check if the user is a administrator
        cls.check_planning_permissions(user, report_data)
        # get the ORM
        report_instance = cls.get_instance(report_data)
        # instance-level validation workflow
        ReportServices.validate_instance(report_instance)

    #########################################
    #          Application Methods          #
    #########################################
