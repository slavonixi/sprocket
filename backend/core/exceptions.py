from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class BusinessLogicError(APIException):
    """
        Business-logic violation. Provide error message when called
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An error occured while processing business logic")
    default_code = "business_logic_error"


class ResourceConflictError(APIException):
    """
    Error for status conflicts
    Can be used for online synchronization of UUID
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = _("A conflict occurred")
    default_code = "resource_conflict"


class ServiceUnavailableError(APIException):
    """
    Errore per problemi con servizi esterni o periferiche (HTTP 503 Service Unavailable).
    Esempio: stampante di etichette offline in officina.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _("Il servizio esterno richiesto non è temporaneamente disponibile.")
    default_code = "service_unavailable"
