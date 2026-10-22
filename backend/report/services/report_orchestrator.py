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

    SUPERVISOR_ONLY_FIELDS_REPORT = (
        'status',
        'date_started',
        'date_closed',
        'synced_at',
    )

    SUPERVISOR_ONLY_FIELDS_OPERATION = (
        'status',
        'execution_start_date',
        'execution_end_date',
        'hours_spent',
        'synced_at',
    )


    #########################################
    #            Utils Methods              #
    #########################################

    @classmethod
    def is_user_authenticated(cls, user):
        if not user or not user.is_authenticated:
            raise BusinessLogicError(
                _("You must be authenticated")
            )

    ################################################
    #    REPORT Permissions Validation Methods     #
    ################################################

    @classmethod
    def check_report_override_permissions(cls, user, report_data):
        """
            Is user trying to do an operations which require supervisor's permissions?
        """
        # check if user has supervisor's perms
        is_supervisor = user.has_perm('report.can_override_report')

        # Which protected fields did the user insert?
        protected_fields = [
            field for field in cls.SUPERVISOR_ONLY_FIELDS_REPORT
            if field in report_data
        ]

        if protected_fields and not is_supervisor:
            raise BusinessLogicError(
                _("You can't insert these fields in the report")
            )

        return is_supervisor

    @classmethod
    def check_report_planning_permissions(cls, user, report_data):
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

    @classmethod
    def validate_report_permissions(cls, user, report_data):
        # check if the creation is being managed by a supervisor
        if not cls.check_report_override_permissions(user, report_data):
            # if not, check if the user is an administrator
            # if is a technician, eventually corrects wrong/forbidden fields
            cls.check_report_planning_permissions(user, report_data)



    ###################################################
    #    OPERATION Permissions Validation Methods     #
    ###################################################

    def check_operation_override_permissions(cls, user, operation_data)
    """
        Is user trying to do an operations which require supervisor's permissions?
    """
    # check if user has supervisor's perms
    is_supervisor = user.has_perm('report.can_override_report')

    # Which protected fields did the user insert?
    protected_fields = [
        field for field in cls.SUPERVISOR_ONLY_FIELDS_OPERATION
        if field in operation_data
    ]

    if protected_fields and not is_supervisor:
        raise BusinessLogicError(
            _("You can't insert these fields in the operation")
        )
    return is_supervisor

    def check_operation_planning_permissions(cls, user, operation_data):
        is_admin = user.has_perm('report.can_plan_report')

        if not is_admin:
            # If the user is a technician, the operation
            # starts immediately
            operation_data['start_now'] = True
        else:
            # If the user is an admin, the operation
            # is simply being planned
            operation_data['start_now'] = False

    @classmethod
    def validate_operation_permissions(cls, user, operation_data):
        # check if the creation is being managed by a supervisor
        if not cls.check_operation_override_permissions(user, operation_data):
            # If not, start the standard validation workflow
            # admin vs technician
            cls.check_operation_planning_permissions(user, operation_data)

    #########################################
    #           Business Methods            #
    #########################################

    @classmethod
    def create_report_and_operation(cls, user, report_data):
        # Check permissions for record
        cls.validate_report_permissions(user, report_data)
        # extract operation's data
        operation_data = report_data.get('operation') or {}
        start_now = None # operation's flag

        # if operation is being contestually creted,
        # start permission validation for it too
        if operation_data:
            cls.validate_operation_permissions(user, operation_data)


        # instance validation -> normalization -> saving
        # through report-operation domain service
        ReportServices.create_report(report_data, operation_data)

    @classmethod
    def add_operation(cls, user, operation_data):
        cls.validate_operation_permissions(user, operation_data)


    @classmethod
    def create_empty_report(cls, user, report_data):
