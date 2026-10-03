from celery import shared_task
from django.utils.translation import gettext_lazy as _

@shared_task
def debug(x, y):
    return x+y

#Crea funzione per loggare

        

@shared_task
def database_celery_log(result):
    """
    
    """
    return result
#REFACTOR -> log a JSON and create a set of methods to print it in UI
#           - also change the "result" method from inventory_services
#{
#  "action": "inventory_withdrawal",
#  "data": {
#    "element_id": "uuid-del-materiale",
#    "withdrawed_qty": 10.5,
#    "measure_unit_symbol": "kg",
#    "final_qty": 89.5
#  },
#  "context": {
#    "technician_id": 45,
#    "report_id": 120
#  }
#}
#
@shared_task
def update_withdraw_log(withdrawed_qty, final_qty):
    pass
@shared_task
def delete_withdraw_log(aborted_qty, final_qty):
    pass