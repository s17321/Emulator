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

# Polecenie uruchamiające oba procesy (emulator i aplikację FastAPI)
CMD ["sh", "-c", "python emulator/emulator.py --all & uvicorn app.main:app --host 0.0.0.0 --port 8080"]