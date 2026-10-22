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
        report_data.pop('publish_immediately')
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

    def validate_report(report_orm, publish_now):
        """
            Performs report's validation and normalization:
                - set report' status
        """
        report_orm.set_status(bool(operation_orm), publish_now)

    def validate_operation(operation_orm, start_now):
        operation_orm.set_status(start_now)

    #########################
    #   BUSINESS METHODS    #
    #########################

    @classmethod
    def create_report(cls, report_data, operation_data):
        """
            validation report + operation
                TODO:
                    - status and op_exists

        """
        # extracts flags
        publish_now = report_data.get('publish_immediately')
        start_now = report_data.get('operation').get('start_now') or None

        # getting ORM instances (from dicts)
        report_orm = cls.get_report_ORM(report_data)
        # Operation ORM is created only if operation_date IS NOT '{}' (so the user choosed to create no operations)
        operation_orm = (
            cls.get_operation_ORM(operation_data) if operation_data else None
        )

        # business logic validation and normalization phase
        # set report's status --> validate_report()

        report_orm.set_status(bool(operation_orm), publish_now)

        # report end -> operation validation
        operation_orm.report_fk = report_orm


        with transaction.atomic():
            report_orm.save()

    def create_operation(operation_data, start_now : Bool):
        # retrieve start now flag
        start_now = operation_data.get("start_now") or None
        # turns the dict into an ORM
        operation_orm = cls.get_operation_ORM(operation_data)
        # normalization/validation
        cls.validate_operation(operation_orm)
        # create_operation
        # add transaction.atomic()
        operation_orm.save()
