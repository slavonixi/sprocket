from celery import shared_task

@shared_task
def debug(x, y):
    return x+y

#Crea funzione per loggare

        
        
#def withdraw_inventory_log()
#def update_withdraw_log()
#def delete_withdraw_log()