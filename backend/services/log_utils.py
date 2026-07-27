from functools import wraps
from rest_framework.exceptions import APIException
from api import tasks

#edit and test this method to return both exceptions
#and JSON method's results



def celery_log_exception(func):
    """Provide automatic exceptions log in database via celery
    - only suitable for APIExceptions
    
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIException as e:
            tasks.database_celery_log.delay(e.detail)
            raise e
    return wrapper

