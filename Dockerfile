FROM python:3.13

# 1. Impostiamo variabili d'ambiente per Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Definizione della cartella di lavoro (FONDAMENTALE per evitare errori di percorso)
WORKDIR /sprocket

# 3. Installazione dipendenze di sistema (necessarie per PostgreSQL e lo script entrypoint)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 4. Installazione delle dipendenze Python (fatta prima per sfruttare la cache di Docker)
COPY requirements.txt /sprocket/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia di tutto il codice del progetto nella cartella /sprocket
COPY . /sprocket/

# 6. Gestione dello script entrypoint (ora che il file è stato sicuramente copiato)
RUN chmod +x /sprocket/entrypoint.sh

# 7. Esposizione della porta per Django (DRF)
EXPOSE 8000
EXPOSE 54320
# 8. Definizione dell'ENTRYPOINT per gestire migrazioni e attesa DB
ENTRYPOINT ["/sprocket/entrypoint.sh"]

WORKDIR /sprocket/backend

# 9. COMANDO FINALE con binding a 0.0.0.0:8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]