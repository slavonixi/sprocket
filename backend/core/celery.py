import os
from celery import Celery
# Imposta il modulo delle impostazioni di Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # Sostituisci 'api' con il nome della tua cartella principale

app = Celery('sprocket')

# QUESTA RIGA È FONDAMENTALE:
# Indica a Celery di leggere tutte le variabili che iniziano con 'CELERY_' nel file settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



