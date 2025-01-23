# app/main.py

import uvicorn
import asyncio
import math
import time
from fastapi import FastAPI
from .config import BRAMKI
from .routers.devices_router import router as devices_router

# Jednorazowy import z pliku can_client – zarówno start_can_client, jak i send_command_to_b
from can_gateway.can_client import start_can_client, send_command_to_b
# router z obsługą wielobramkowych endpointów
from .routers.devices_router import router as devices_router

# Import routerów
from .routers.device_a_router import router as device_a_router
from .routers.device_b_router import router as device_b_router
from .routers.module_c_router import router as module_c_router

# Wspólny "schowek" na gniazdo socket i stany (device_a_state, device_b_state, module_c_state)
from . import state


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """
    Uruchamia się, gdy aplikacja wystartuje.
    1) Łączymy się z emulatorem (lub z prawdziwą bramką CAN-TCP),
    2) Zapisujemy socket w state.client_socket,
    3) Uruchamiamy w tle task do automatycznego resetowania watchdog w B.
    """
    # host = "127.0.0.1"
    # port = 5000
    # new_socket = start_can_client(host, port)  # łączy się z emulatorem
    # state.client_socket = new_socket
    # print("[MAIN] CAN client started, connected to emulator.")

    for bramka_conf in BRAMKI:
        bramka_name = bramka_conf["name"]
        host = bramka_conf["host"]
        port = bramka_conf["port"]

        sock = start_can_client(host, port, bramka_name)
        if sock:
            state.bramki_sockets[bramka_name] = sock
            print(f"[MAIN] Connected to {bramka_name} at {host}:{port}.")
        else:
            print(f"[MAIN] Failed to connect to {bramka_name}. Starting reconnect task...")
            asyncio.create_task(reconnect_socket(bramka_conf))

    # Uruchamiamy w tle pętlę automatycznych zadań
    asyncio.create_task(automatic_watchdog_reset_task())
    asyncio.create_task(module_c_task())
    print("[MAIN] module_c_task started.")
    print("[MAIN] Startup done.")


async def automatic_watchdog_reset_task():
    """
    Co 500 ms wysyłamy ramkę resetującą watchdog w B (ID=0x200, payload=0x01).
    """
    while True:
        for bramka_name, sock in state.bramki_sockets.items():
            # Wysyłamy ramkę do ID=0x200, payload = [0x01]
            # Oczywiście, jeśli dana bramka realnie obsługuje urządzenie B
            # (możesz dodać if weryfikujące, czy w config jest "B" w bramka_conf["devices"])
            if sock:  # Sprawdzamy, czy socket jest poprawny
                send_command_to_b(sock, 0x200, bytes([0x01]))
            else:
                print(f"[MAIN] Cannot reset watchdog for {bramka_name}: socket is None.")
        await asyncio.sleep(0.5)  # co 500 ms -- poki co jest 10s

async def module_c_task():
    """
    Funkcja co 100 ms pobiera rejestry A i B
    i oblicza np. last_result = (a_reg1 + b_reg1) * param_x * sin(current_time).
    Wartość zapisuje w state.module_c_state.
    """
    while True:
        now = time.time()
        for bramka_name in state.bramki_sockets.keys():
            keyA = f"A_{bramka_name}"
            keyB = f"B_{bramka_name}"

            if keyA in state.devices_state and keyB in state.devices_state:
                a_reg1 = state.devices_state[keyA].register_1
                b_reg1 = state.devices_state[keyB].register_1
                # obliczenia w czasie rzeczywistym:
                result = (a_reg1 + b_reg1) * state.module_c_state.param_x * math.sin(now)

                # Zapis do slownika results
                state.module_c_state.results[bramka_name] = result
            else:
                # Może brakować jednego z urządzeń; co wtedy?
                state.module_c_state.results[bramka_name] = -999.0  # np. brak danych
        await asyncio.sleep(0.1)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Wywoływane przy zamykaniu aplikacji (np. Ctrl+C).
    Zamykamy socket, aby uprzątnąć zasoby.
    """
    for bramka_name, sock in state.bramki_sockets.items():
        if sock:
            try:
                sock.close()
                print(f"[MAIN] Socket closed for {bramka_name}.")
            except Exception as e:
                print(f"[MAIN] Error while closing socket for {bramka_name}: {e}")
    state.bramki_sockets.clear()
    print("[MAIN] All sockets closed.")


@app.get("/")
def root():
    return {"message": "Hello from APP"}

async def reconnect_socket(bramka):
    """
    Próbuje ponownie połączyć socket dla bramki.
    """
    while True:
        sock = start_can_client(bramka["host"], bramka["port"], bramka["name"])
        if sock:
            state.bramki_sockets[bramka["name"]] = sock
            print(f"[CAN_CLIENT] Reconnected to {bramka['name']}.")
            break
        print(f"[CAN_CLIENT] Reconnect failed for {bramka['name']}. Retrying in 5 seconds...")
        await asyncio.sleep(5)


# Podpinamy routery
app.include_router(device_a_router)
app.include_router(device_b_router)
app.include_router(module_c_router)
app.include_router(devices_router)


if __name__ == "__main__":
    # uvicorn app.main:app --reload
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
