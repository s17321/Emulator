# Użyj obrazu bazowego Pythona
FROM python:3.11

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj plik requirements.txt do kontenera
COPY requirements.txt /app/

# Skopiuj cały katalog my_app do kontenera
COPY my_app /app/my_app

# Zainstaluj zależności
RUN pip install --no-cache-dir -r requirements.txt

# Komenda startowa
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]