import socket
import threading
import time
from typing import Optional

HOST = "127.0.0.1"
PORT = 5000

#zmienne stanu (symulacja rejestrów A i B)
device_a_register_1 = 10
device_a_register_2 = 20

device_b_register_1 = 100
device_b_register_2 = 200
device_b_watchdog_ok = True
device_b_watchdog_timestamp = time.time()  # kiedy ostatnio zresetowano

WATCHDOG_TIMEOUT = 5.0  # np. 5 sekund

def start_emulator(host=HOST, port=PORT):
    """
    Uruchamia serwer TCP nasłuchujący na (host, port),
    który symuluje bramkę CAN-TCP oraz urządzenia A i B.
    """
    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_socket.bind((host, port))
    srv_socket.listen(4)
    print(f"[EMULATOR] Listening on {host}:{port} ...")

    while True:
        client_socket, addr = srv_socket.accept()
        print(f"[EMULATOR] Connection from {addr}")

        # Uruchamiamy wątki:
        # 1. Odbieranie ramek (dla B - reagowanie na polecenia)
        recv_thread = threading.Thread(
            target=handle_client_receive, 
            args=(client_socket,),
            daemon=True
        )
        recv_thread.start()

        # 2. Wysyłanie ramek z A i B (w pętli co jakiś czas)
        send_thread = threading.Thread(
            target=handle_client_send, 
            args=(client_socket,),
            daemon=True
        )
        send_thread.start()

def start_all_emulators():
    ports = [5000, 5001]
    for p in ports:
        threading.Thread(
            target=start_emulator,
            args=("127.0.0.1", p),
            daemon=True
        ).start()
    # Aby wątek główny nie wyszedł natychmiast:
    while True:
        time.sleep(1)


def handle_client_receive(client_socket: socket.socket):
    """
    Pętla odbierająca ramki z clienta (APP).
    Interpretujemy je jako komendy do urządzenia B.
    """
    global device_b_register_1, device_b_register_2
    global device_b_watchdog_ok, device_b_watchdog_timestamp

    try:
        while True:
            data = client_socket.recv(13)  # odbieramy 13 bajtów (1 ramka)
            if not data:
                break  # rozłączenie

            # interpretuj 13-bajtową ramkę
            # [0] = standard/extended,
            # [1] = RTR,
            # [2..5] = ID (4 bajty),
            # [6] = DLC,
            # [7..12] = data (do 6 bajtów + wypełnienie, zależnie od DLC)
            
            # Przyklad interpretacji
            can_id_bytes = data[2:6]     # 4 bajty
            can_id = int.from_bytes(can_id_bytes, byteorder='big')
            dlc = data[6]
            payload = data[7:7+dlc]
            # print(f"[EMULATOR] Rcv ID={hex(can_id)}, DLC={dlc}, payload={payload.hex()}")

            # Jeśli ID = np. 0x200 -> komendy do B
            if can_id == 0x200:
                # ustalmy, że bajt[0] = kod polecenia
                if dlc > 0:
                    cmd = payload[0]
                    if cmd == 0x01:
                        # reset watchdog
                        device_b_watchdog_timestamp = time.time()
                        device_b_watchdog_ok = True
                        # print("[EMULATOR] B watchdog reset via command")
                    elif cmd == 0x02 and dlc >= 3:
                        # np. Ustaw rejestr_1 -> kolejne 2 bajty w payload
                        new_val = int.from_bytes(payload[1:3], byteorder='big')
                        device_b_register_1 = new_val
                        # print(f"[EMULATOR] B register_1 = {new_val}")
                    else:
                        # inne komendy ... 
                        pass
    except Exception as e:
        print(f"[EMULATOR] handle_client_receive exception: {e}")
    finally:
        client_socket.close()
        print("[EMULATOR] Client disconnected (receive)")


def handle_client_send(client_socket: socket.socket):
    """
    Pętla wysyłająca ramki co pewien czas, aby symulować:
    - Urządzenie A (raport stanu)
    - Urządzenie B (raport stanu)
    - Sprawdzanie watchdog
    """
    global device_a_register_1, device_a_register_2
    global device_b_register_1, device_b_register_2
    global device_b_watchdog_ok, device_b_watchdog_timestamp

    try:
        while True:
            # 1. Sprawdź watchdog B
            if time.time() - device_b_watchdog_timestamp > WATCHDOG_TIMEOUT:
                device_b_watchdog_ok = False

            # 2. Wyślij ramkę od A (np. ID = 0x100) 
            #    co sekunda z danymi rejestrów
            # Format: 13 bajtów
            # [0] = 0 -> standard
            # [1] = 0 -> data frame
            # [2..5] = ID (0x100)
            # [6] = DLC (np. 4)
            # [7..10] = dane (np. rejestry A)
            
            frame_a = bytearray(13)
            frame_a[0] = 0  # standard
            frame_a[1] = 0  # data
            frame_a[2:6] = (0x100).to_bytes(4, byteorder='big')
            frame_a[6] = 4  # DLC
            frame_a[7:9] = device_a_register_1.to_bytes(2, byteorder='big')
            frame_a[9:11] = device_a_register_2.to_bytes(2, byteorder='big')
            
            client_socket.sendall(frame_a)

            # 3. Wyślij ramkę od B (ID = 0x101)
            # Wstaw w payload rejestry B + status watchdog
            frame_b = bytearray(13)
            frame_b[0] = 0
            frame_b[1] = 0
            frame_b[2:6] = (0x101).to_bytes(4, byteorder='big')
            frame_b[6] = 5  # DLC = 5
            frame_b[7:9] = device_b_register_1.to_bytes(2, byteorder='big')
            frame_b[9:11] = device_b_register_2.to_bytes(2, byteorder='big')
            frame_b[11] = 1 if device_b_watchdog_ok else 0
            client_socket.sendall(frame_b)

            time.sleep(1.0)  # co 1s wysyłamy pakiety A i B

    except Exception as e:
        print(f"[EMULATOR] handle_client_send exception: {e}")
    finally:
        client_socket.close()
        print("[EMULATOR] Client disconnected (send)")

def check_watchdog_b():
    global device_b_watchdog_ok, device_b_watchdog_timestamp
    if time.time() - device_b_watchdog_timestamp > WATCHDOG_TIMEOUT:
        device_b_watchdog_ok = False

if __name__ == "__main__":
    # start_emulator()
    start_all_emulators()