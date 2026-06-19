FROM python:3.13

# Impostiamo variabili d'ambiente per Python (ottimizzazione Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Setup utente prima di copiare i file

# Installa le dipendenze
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice e cambia il proprietario a 'salvo'
COPY . .

# Passa all'utente salvo

# Esponi la porta (Django usa solitamente la 8000)
EXPOSE 8000
EXPOSE 54320

# Comando corretto con sintassi corretta e binding all'IP 0.0.0.0
