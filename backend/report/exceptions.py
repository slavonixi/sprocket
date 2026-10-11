from rest_framework.exceptions import APIException #pyright: ignore
from rest_framework import status #pyright: ignore
from django.utils.translation import gettext_lazy as _


def buildMessage(*, status="failed", operation="not specified", code, **kwargs):

    data = {}
    for key, value in kwargs.items():
        data[key] = value
    message = {
        "status": status,
        "operation": operation,
        "code": code,
        "data": data,
    }
    return message

class ReportError(APIException):
    """Parent class for the report errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Exception.Report'

class OperationError(APIException):
    """Parent class for the operations errors"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Exception.Operation'

class IllegalReportStatus(ReportError):
    """
        report cannot be in this status at the moment
    """
    def __init__(self, illegal_status, op='report_edit_or_create'):
        data = {
            'illegal_status' : illegal_status
        }
        result = buildMessage(
            operation=op,
            code = self.default_detail,
            **data
        )
        super().__init__(result)

class DateError(ReportError):
    """
        date open and date close must follow these rules:
            - date close must be None on creation
    """
    def __init__(self, illegal_date, op='report_edit_or_create'):
        data = {
            'status' : illegal_date,
        }
        result = buildMessage(
            operation=op,
            code = self.default_detail,
            **data
        )
        super().__init__(result)


class CustomerIsNone(ReportError):
    """
       customer must be set when creating a report
    """
    def __init__(self, op='report_edit_or_create'):
        result = buildMessage(
            operation=op,
            code = self.default_detail+'.CustomerIsNone',
        )
        super().__init__(result)



############################
#    OPERATION ERRORS      #
############################

class IllegalOperationStatus(OperationError):
    """
        operation instance cannot be in this status at the moment
    """
    def __init__(self, illegal_status, op='operation_edit_or_create'):
        data = {
            'status' : illegal_status
        }
        result = buildMessage(
            operation=op,
            code = self.default_detail+'.IllegalOperationStatus',
            **data
        )
        super().__init__(result)

class TechniciansRequired(OperationError):
    """
        Technicians are not set, but they should be assigned at this task
    """
    def __init__(self, op='operation_edit_or_create'):
        result = buildMessage(
            operation=op,
            code = self.default_detail+'.TechniciansRequired',
        )
        super().__init__(result)

class PermissionDenied(OperationError):
    """
     You missing the permissions to perform an action 
    """
    def __init__(self, op='operation_edit_or_create'):
        result = buildMessage(
            operation=op,
            code = self.default_detail+'.PermissionDenied',
        )
        super().__init__(result)    