# Użyj obrazu bazowego Pythona
FROM python:3.11

# Ustaw katalog roboczy w kontenerze
WORKDIR /my_app

# Kopiowanie pliku requirements.txt i instalacja zależności
COPY requirements.txt /my_app/
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie całej aplikacji do kontenera
COPY . /my_app/

# Polecenie uruchamiające oba procesy
CMD ["sh", "-c", "python emulator/emulator.py --all & uvicorn app.main:app --host 0.0.0.0 --port 8000"]