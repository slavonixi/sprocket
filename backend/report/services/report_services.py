from django.db import transaction
from django.utils import timezone
from core.exceptions import BusinessLogicError


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
    def get_report_ORM(report_data):
        """
            Translate a dict into a ready-to-use Report ORM
        """
        report_data.pop('operation')
        report_data.pop('publish_now')
        report_orm = Report(**report_data)
        return report_orm

    @classmethod
    def get_operation_ORM(operation_data):
        """
            Translate a dict into a ready-to-use Operation ORM
        """
        if operation_data.get("start_now"):
            operation_data.pop("start_now")
        operation_orm = Operation(**operation_data)
        return operation_orm


    ###################################
    #   VALIDATION & NORMALIZATION    #
    ###################################

    @classmethod
    def can_add_operation_to_report(report_orm):
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
                _("The operation must be associated to a report")
            )

    #########################
    #    PUBLIC METHODS     #
    #########################

    @classmethod
    @transaction.atomic
    def new_report(cls, report_data, operation_data):
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

        # get operation ORM
        operation_orm = cls.get_operation_ORM(operation_data)

        # is the report open?
        cls.can_add_operation_to_report(operation_orm.report_fk)

        # set status
        initial_status = operation_orm.calculate_initial_status(start_now)
        operation_orm.status = initial_status

        # create_operation
        operation_orm.save()
        return True

    @classmethod
    @transaction.atomic
    def new_report_with_operation(cls, report_data, operation_data):
        # retrieve flags
        start_now = operation_data.get('start_now')
        publish_now = report_data.get('publish_now')

        # get ORMs
        operation_orm = cls.get_operation_ORM(operation_data)
        report_orm = cls.get_report_ORM(report_data)

        # attach operation to the parent report
        operation_orm.report_fk = report_orm

        # set status
        operation_initial_status = operation_orm.calculate_initial_status(start_now)
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
