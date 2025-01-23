# Użyj obrazu bazowego Pythona
FROM python:3.11

# Ustaw katalog roboczy w kontenerze
WORKDIR /my_app

# Kopiowanie pliku requirements.txt
COPY my_app/requirements.txt /my_app/

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie całej aplikacji
COPY my_app/ /my_app/

# Zainstaluj supervisord
RUN apt-get update && apt-get install -y supervisor && apt-get clean

# Skopiuj konfigurację supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Komenda startowa
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]