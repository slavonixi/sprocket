# SERVICES
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
    """
    Public methods of the orchestrator:
        -> create_empty_report
            Who calls it?
            - viewset: Report
            - endpoint(@action): plan   (is_planning always True)
            - checks if operation's nested serializer is provided.
              if not, an admin is creating an empty report and so
              calls this method
        -> create_report_and_operation
            Who calls it?
            - viewset: Report
            - endpoint: plan/start
            - called only if operation's nested serializer is provided
            - endpoint 'plan' -> is_planning=True [admins]
            - endpoint 'start' -> is_planning=False [techns.]
        -> add_operation
            Who calls it?
            - viewset: Operation
            - endpoint: plan/start
            - add operation into and EXISTING report
            - endpoint 'plan' -> is_planning=True [admins]
            - endpoint 'start' -> is_planning=False [techns.]

    """

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
        Check if the user is trying to insert protected fields
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
    def check_report_starting_permissions(cls, user, report_data):
        """
        Check if the user has the permission to quick-start a report
        (report + operation(start) creation [intended for technicians])
        """
        # check if the user can start reports
        is_tech = user.has_perm('report.can_start_report')


        if is_tech:
            # if the user has the perms, setup the flag to quickstart
            report_data['publish_now'] = True
        else:
            raise BusinessLogicError(
                _("You dont have the permissions to quick-start a report")
            )
        return report_data


    @classmethod
    def check_report_planning_permissions(cls, user, report_data):
        """
        Check if the user has the perms to plan a report (empty or w/operation)
        """
        # check if the user can plan reports
        is_admin = user.has_perm('report.can_plan_report')

        if is_admin:
            report_data.setdefault('publish_now', False)
        else:
            raise BusinessLogicError(
                _("You dont have the permissions to plan a report")
            )
        return report_data

    @classmethod
    def get_validated_report_data(cls, user, report_data, is_planning):
        """
        Check for permissions and normalize report_data.
            - if the user is a supervisor, let him insert custom fields
            - if the user is trying to plan (is_planning = True), check if
              he has admin's perms
            - if the user is trying to quickstart (is_planning = False) check
              if he has technician's perms
        """
        # check if the creation is being managed by a supervisor
        is_supervisor = cls.check_report_override_permissions(user, report_data)
        if not is_supervisor:
            # if not, check wether is trying to plan or not
            if is_planning:
                # if yes, check admin permissions and normalize report_data
                # in order to plan a report
                report_data = cls.check_report_planning_permissions(user, report_data)
            else:
                # if not, check for technician permissions and normalize report_data
                # in order to quickstart report+operation
                report_data = cls.check_report_starting_permissions(user, report_data)
        return report_data


    ###################################################
    #    OPERATION Permissions Validation Methods     #
    ###################################################

    @classmethod
    def check_operation_override_permissions(cls, user, operation_data):
        """
        Check if the user is trying to insert protected_fields
        """
        # check if user has supervisor's perms
        is_supervisor = user.has_perm('operation.can_override_operation')

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

    @classmethod
    def check_operation_planning_permissions(cls, user, operation_data):
        """
        Check if the user has admin's perms and normalize operation_data
        in order to plan the operation
        """
        is_admin = user.has_perm('operation.can_plan_operation')

        if is_admin:
            # if perms are ok, the operation is set to not
            # start in this moment (planning)
            operation_data['start_now'] = False
        else:
            raise BusinessLogicError(
                _("You don't have the permission to schedule an operation")
            )

    @classmethod
    def check_operation_starting_permissions(cls, user, operation_data):
        """
        Check if the user has technician perms and normalize operation_data
        in order to start an operation
        """
        is_tech = user.has_perm('operation.can_start_operation')

        if is_tech:
            # If the user is a technician, the operation
            # starts immediately
            operation_data['start_now'] = True
            # secure planning fields as scheduled_datetime
            operation_data['scheduled_datetime'] = None
            # retrieve technician profile if it isn't set
            report_data.setdefault('technicians', user.hr_record)
        else:
            raise BusinessLogicError(
                _("You don't have the permission to start an operation")
            )
        return operation_data

    @classmethod
    def get_validated_operation_data(cls, user, operation_data, is_planning=False):
        """
        Check for permissions and normalize operation_data.
            - if the user is a supervisor, let him insert custom protected_fields
            - if the user's trying to plan an operation (is_planning=True), check if
              he has admin's perms, then normalize operation_data
            - if the user is trying to start an operation (is_planning=False), check if
              he has tehcnician's perms, then noralize operation data
        """
        # check if the creation is being managed by a supervisor
        is_supervisor = cls.check_operation_override_permissions(user, operation_data)
        if not is_supervisor:
            # if not, check if the user is tryin to plan
            if is_planning:
                # check for admin's perms and normalize
                operation_data = cls.check_operation_planning_permissions(user, operation_data)
            else:
                # check for technician's perms and normalize
                operation_data = cls.check_operation_starting_permissions(user, operation_data)
        return operation_data

    #########################################
    #           Business Methods            #
    #########################################

    @classmethod
    def create_report_and_operation(cls, user, report_data, *, is_planning=False):
        """
        Workflow to create report+operation.
          - if is_planning=True the user called the endpoint for planning
          and then there'll be checked admin perms
          - if is_planning=False the user called the endpoint for quickstart
          report+operation and then there'll be checked technician's perms
        """

        # Check permissions for record
        report_data = cls.get_validated_report_data(user, report_data, is_planning)

        # extract operation's data
        operation_data = report_data.get('operation') or {}

        # operation_data must be provided from the POST request
        if not operation_data: # otherwise, raise an Exception
            raise BusinessLogicError(
                _("Operation data must be inserted during a combined creation")
            )

        # check permissions and get normalized operation dict
        operation_data = cls.get_validated_operation_data(user, operation_data)

        # crete report + operation domain logic
        ReportServices.new_report_with_operation(report_data, operation_data)

    @classmethod
    def add_operation(cls, user, operation_data, is_planning=False):
        """
        Create an operation and add it to an existing report.
            - is_planning = True: admin's permission
            - is_planning = False: (technician on field) tech's permissions
        """
        # permission validation and dict normalization
        operation_data = cls.get_validated_operation_data(user, operation_data, is_planning)
        # operation creation domain service
        ReportServices.add_operation(operation_data)

    @classmethod
    def create_empty_report(cls, user, report_data):
        """
        Empty report creation (intended only for administrators)
        """
        # validate permissions and get normalized dict
        # only admins can create empty report, so that is_planning = true
        report_data = cls.get_validated_report_data(user, report_data, True)
        # report create domain logic
        ReportServices.create_report(report_data)

    #     #############################################
    #############################################
    #     #############################################
    #############################################
    #     #############################################

   # cosa devi fare domani:
       # 1. creare 4 endpoint distinti con @action (plan/start operation/report)
       # 3. le action di report avranno il check per capire se è report o report+op
       # 4. iniziare a testare report_services
