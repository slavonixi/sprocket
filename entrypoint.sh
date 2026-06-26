#!/bin/sh

# Attende che PostgreSQL sia pronto (importante per evitare crash all'avvio)
echo "In attesa di PostgreSQL..."
while ! nc -z postgres_db 5432; do
  sleep 0.1
done
echo "PostgreSQL avviato."

# Esegue le migrazioni del database
echo "Applicazione delle migrazioni..."
python manage.py makemigrations
python manage.py migrate

# Crea le tabelle specifiche per i risultati di Celery
python manage.py migrate django_celery_results

# Raccoglie i file statici (necessario per l'interfaccia Admin e DRF)
python manage.py collectstatic --no-input

# (Opzionale) Crea un superuser automaticamente se non esiste
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'password_segreta')"

# Avvia il server Django
exec "$@"
