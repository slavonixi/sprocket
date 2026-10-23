from django.db import transaction
from django.utils import timezone
from core.exceptions import BusinessLogicError
from django.utils.translation import gettext_lazy as _


# MODELS
from report.models import (
    Report,
    Operation,
)


class ReportServices:

    #########################
    #     UTILS METHODS     #
    #########################

    @classmethod
    def get_report_ORM(cls, report_data):
        """
            Translate a dict into a ready-to-use Report ORM
        """
        report_data.pop('operation', None)
        report_data.pop('publish_now', None)
        report_orm = Report(**report_data)
        return report_orm

    @classmethod
    def get_operation_ORM(cls, operation_data):
        """
            Translate a dict into a ready-to-use Operation ORM
        """
        operation_data.pop("start_now", None)
        operation_data.pop("technicians", None)
        operation_orm = Operation(**operation_data)
        return operation_orm


    ###################################
    #   VALIDATION & NORMALIZATION    #
    ###################################

    @classmethod
    def can_add_operation_to_report(cls, report_orm):
        """
        Check if report_fk (report_orm) is valid and accept
        operation
        """
        if hasattr(report_orm, 'is_open_for_operations'):
            if report_orm.is_open_for_operations:
                return True
            else:
                raise BusinessLogicError(
                    _("The report is not open for new operations")
                )
        else:
            raise BusinessLogicError(
                _("The operation must be associated to an existent report")
            )

    @classmethod
    def operation_business_validation(cls, operation_orm : Operation, start_now : bool, has_technicians : bool):

        if start_now:
            # check if the operation has technicians assigned
            if not has_technicians:
                raise BusinessLogicError(
                    _("Can't start an operation without technicians")
                )
            # check if the operation scheduled date is not set
            if operation_orm.scheduled_datetime:
                raise BusinessLogicError(
                    _("scheduled date and start now conflict")
                )



    #########################
    #    PUBLIC METHODS     #
    #########################

    @classmethod
    @transaction.atomic
    def new_empty_report(cls, report_data):
        """
            validation report + operation
                TODO:
                    - status and op_exists

        """
        # retrieve flag
        publish_now = report_data.get('publish_now')

        # get report ORM
        report_orm = cls.get_report_ORM(report_data)

        # set status
        initial_status = report_orm.calculate_initial_status(
            publish_now = publish_now,
            has_operations = False,
        )
        report_orm.status = initial_status

        # create empty report
        report_orm.save()
        return True

    @classmethod
    @transaction.atomic
    def add_operation_to_report(cls, operation_data):
        # retrieve start now flag
        start_now = operation_data.get("start_now")

        # retrieve technicians
        technicians_list = operation_data.pop('technicians', None)

        # get operation ORM
        operation_orm = cls.get_operation_ORM(operation_data)

        # is the report open?
        cls.can_add_operation_to_report(operation_orm.report_fk)
        # standard business validation
        cls.operation_business_validation(operation_orm, start_now, bool(technicians_list))

        # set status
        initial_status = operation_orm.calculate_initial_status(start_now, bool(technicians_list))
        operation_orm.status = initial_status

        # create_operation
        operation_orm.save()

        # set technicians
        if technicians_list:
            operation_orm.technicians.set(technicians_list)

        return operation_orm

    @classmethod
    @transaction.atomic
    def new_report_with_operation(cls, report_data, operation_data):
        # retrieve flags
        start_now = operation_data.get('start_now')
        publish_now = report_data.get('publish_now')

        # get technicians list
        technicians_list = operation_data.pop('technicians', None)

        # get ORMs
        operation_orm = cls.get_operation_ORM(operation_data)
        report_orm = cls.get_report_ORM(report_data)

        # attach operation to the parent report
        operation_orm.report_fk = report_orm

        # operation's business validation
        cls.operation_business_validation(operation_orm, start_now, bool(technicians_list))

        # set status
        operation_initial_status = operation_orm.calculate_initial_status(start_now, bool(technicians_list))
        operation_orm.status = operation_initial_status
        report_initial_status = report_orm.calculate_initial_status(
            publish_now=publish_now,
            has_operations=True,
            is_planned=operation_orm.is_planned
        )
        report_orm.status = report_initial_status

        # create
        report_orm.save()
        operation_orm.save()

        # assign technicians
        if technicians_list:
            operation_orm.technicians.set(technicians_list)

        return {
            'report': report_orm,
            'operation': operation_orm,
        }
