1. Wprowadzenie
Projekt ma na celu symulację i obsługę systemu składającego się z dwóch urządzeń (A i B) komunikujących się przez bramki CAN-TCP. 
Aplikacja APP - to nasz serwis. 

-Udostępnia interfejs (API) do komunikacji z użytkownikiem za pomocą FastAPI
-Pozwala monitorować stan trzech "obiektów" Urządzeń A i B oraz Modułu C.
-Umożliwia wysyłanie poleceń do Urządzenia B (zmiana parametrów x i y)
-W aplikacje jest wbudowany algorytm sterowania z możliwością zmiany parametrów. 
-Moduł C działa w czasie rzeczywistym. Obliczenia są wykonywane co 0,1s.
-Emulator urządzeń A i B.

2. Architektura i główne elementy
Emulator (A i B) – Nasłuchuje na porcie TCP, wysyła ramki z danymi urządzeń A (ID=0x100) i B (ID=0x101), przyjmuje polecenia (ID=0x200) dla B.
Aplikacja FastAPI (APP) – Uruchomiona lokalnie. Składa się z:
-Klienta TCP (can_gateway), który łączy się do emulowanych bramek (lub prawdziwych).
-Routerów (device_a_router, device_b_router, module_c_router) obsługujących endpointy REST.
-Stanu aplikacji (app/state.py) przechowującego dane o urządzeniach (registery, watchdog, parametry modułu C).

Zadań w tle (background tasks):
-Watchdog resetujący urządzenie B co 500ms,
-Moduł C obliczający coś co 100ms z rejestrów A i B.

Interfejs API – Umożliwia:
-Odczyt stanu A, B, modułu C (GET /device-a/..., GET /device-b/..., GET /module-c/...),
-Sterowanie urządzeniem B (POST /device-b/command),
-Konfigurację modułu C (POST /module-c/config).

Testy (Pytest) – automatyczne testy logiki - test_module_c_logic

Frontend – Streamlit do prezentacji aplikacji oraz do sterowania.


3. Instrukcja uruchamiania
cd my_app
(Opcjonalnie) utwórz wirtualne środowisko:
python -m venv venv

source venv/bin/activate  # linux/mac
lub 
.\venv\Scripts\activate  # windows

Zainstaluj zależności:
pip install -r requirements.txt

3.2. Uruchamianie emulatorów
Emulator może działać na jednym lub wielu portach (np. 5000, 5001). 

Uruchomienie w jednym procesie – start_all_emulators() w emulator.py
my_app> python emulator\emulator.py --all

Po odpaleniu zobaczysz w logach np.:

[EMULATOR] Listening on 127.0.0.1:5001 ...
[EMULATOR] Listening on 127.0.0.1:5000 ...

3.3. Uruchamianie aplikacji FastAPI (APP)
W osobnym terminalu:

my_app> python -m uvicorn app.main:app

Zobacz w logach emulatora, że aplikacja łączy się z bramkami (port 5000, 5001). Wyświetli komunikat:
[EMULATOR] Connection from ('127.0.0.1', 55345)
[EMULATOR] Connection from ('127.0.0.1', 55346)

W konsoli aplikacji pojawią się informacje o wysyłanych ramkach

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
[CAN_CLIENT] Sent frame to ID=0x200 with payload=01
[CAN_CLIENT] Sent frame to ID=0x200 with payload=01
[CAN_CLIENT] Received frame from bramka1 - CAN ID: 0x100, DLC: 4, Payload: 000a0014
[CAN_CLIENT] Received frame from bramka1 - CAN ID: 0x101, DLC: 5, Payload: 006400c801


Teraz pod adresem http://127.0.0.1:8000/docs możesz obejrzeć dokumentację Swagger i testowo wywołać endpointy.

4. Najważniejsze endpointy:

Urządzenie A:

GET /device-a/{bramka_name}/state
Zwraca JSON:
{
  "register_1": 10,
  "register_2": 20,
  "status": "OK"
}

Urządzenie B:

GET /device-b/{bramka_name}/state
Zwraca: 
{
  "register_1": 100,
  "register_2": 200,
  "watchdog_ok": true
}

oraz 

POST /device-b/{bramka_name}/command
Przyjmuje JSON :
{
  "command": "set_register",
  "value": 1234
}

lub

{
  "command": "reset_watchdog"
}
Zwraca {"status": "ok"} przy sukcesie.

Moduł C:

GET /module-c/state
Zwraca np:
{
  "param_x": 1,
  "param_y": 2,
  "last_result": 42.000
}

POST /module-c/config
Pozwala ustawić param_x, param_y w ciele zapytania:
{
  "param_x": 3.14,
  "param_y": 2.71
}

Zwraca: {"status":"ok"} 

5. Moduł C i Watchdog
Watchdog w B jest zerowany co 500 ms. Aplikacja w startup_event uruchamia automatic_watchdog_reset_task(), które co 0.5s wysyła ramkę z ID=0x200, payload=0x01 do B.
Moduł C liczy (registerA + registerB) * param_x * sin(t) co 100 ms, a wynik zapisuje w module_c_state.last_result.

6. Testy automatyczne (Pytest)
Uruchamianie testów:

cd my_app
pytest

Testy jednostkowe mogą sprawdzać logikę modułu C, a testy integracyjne korzystają z fastapi.testclient.TestClient.

tests/test_module_c.py – sprawdza poprawność obliczeń param_x, param_y.

7. Frontend (Streamlit)
Plik streamlit_app.py, uruchamiany przez:

streamlit run frontend/streamlit_app.py
Pozwala w przeglądarce (domyślnie http://localhost:8501):

Odczytu stanu A, B, modułu C,
Ustawiania parametrów (np. param_x, param_y),
Wysyłania komend do B (np. set_register).