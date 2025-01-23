# Użyj obrazu bazowego Pythona
FROM python:3.11

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj pliki do kontenera
COPY requirements.txt /app/
COPY ./my_app /app

# Zainstaluj zależności
RUN pip install -r requirements.txt

# Komenda startowa
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]