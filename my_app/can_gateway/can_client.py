import socket
import threading
import time
from app import state

def start_can_client(host, port, bramka_name):
    """ 
    Tworzy socket, łączy się, uruchamia wątek do odbierania ramek. 
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"[CAN_CLIENT] Connected to {bramka_name} on {host}:{port}")

        # Start wątku odbioru
        t = threading.Thread(target=receive_loop, args=(sock, bramka_name), daemon=True)
        t.start()
        return sock
    except ConnectionRefusedError:
        print(f"[CAN_CLIENT] Connection refused for {bramka_name} on {host}:{port}")
        return None
    except Exception as e:
        print(f"[CAN_CLIENT] Unexpected error for {bramka_name}: {e}")
        return None

def receive_loop(sock, bramka_name):
    """ 
    Ramki (13 bajtów) w pętli.
    Na podstawie can_id rozróżniamy czy to dane A (ID=0x100) czy B (ID=0x101).
    Zapisujemy do state.devices_state["A_bramka1"] lub "B_bramka1" itd. 
    """
    try:
        while True:
            frame = sock.recv(13)
            if not frame:
                print(f"[CAN_CLIENT] Empty frame received for {bramka_name}")
                break
            can_id = int.from_bytes(frame[2:6], byteorder='big')
            dlc = frame[6]
            payload = frame[7:7+dlc]
            print(f"[CAN_CLIENT] Received frame from {bramka_name} - CAN ID: 0x{can_id:X}, DLC: {dlc}, Payload: {payload.hex()}")


            # Rozpoznaj, czy to ramka A, B, itp.
            if can_id == 0x100:
                # To np. dane od A
                # Przykładowo 4 bajty danych: reg1, reg2
                reg1 = int.from_bytes(payload[0:2], 'big')
                reg2 = int.from_bytes(payload[2:4], 'big')

                # Klucz "A_bramka1" np.
                key = f"A_{bramka_name}"
                if key not in state.devices_state:
                    state.devices_state[key] = state.DeviceAState()

                # Aktualizujemy
                state.devices_state[key].register_1 = reg1
                state.devices_state[key].register_2 = reg2

            elif can_id == 0x101:
                # Dane od B
                reg1 = int.from_bytes(payload[0:2], 'big')
                reg2 = int.from_bytes(payload[2:4], 'big')
                wd_ok = (payload[4] == 1) if len(payload) >= 5 else False

                key = f"B_{bramka_name}"
                if key not in state.devices_state:
                    state.devices_state[key] = state.DeviceBState()

                # Aktualizujemy
                state.devices_state[key].register_1 = reg1
                state.devices_state[key].register_2 = reg2
                state.devices_state[key].watchdog_ok = wd_ok
            
    except Exception as e:
        print(f"[CAN_CLIENT] receive_loop error for {bramka_name}: {e}")
    finally:
        sock.close()
        print(f"[CAN_CLIENT] Socket closed for {bramka_name}")

def send_command_to_b(sock, cmd_id, payload: bytes):
    """
    Funkcja, aby wysłać ramkę do B przez emulator
    np. cmd_id=0x200, reset watchdog lub ustaw rejestr
    """
    if sock is None:
        print(f"[CAN_CLIENT] Cannot send frame to ID=0x{cmd_id:X}: socket is None.")
        return
    
    try:
        frame = bytearray(13)
        frame[0] = 0   # standard frame
        frame[1] = 0   # data frame
        frame[2:6] = cmd_id.to_bytes(4, byteorder='big')
        frame[6] = len(payload)  # DLC
        frame[7:7+len(payload)] = payload

        sock.sendall(frame)
        print(f"[CAN_CLIENT] Sent frame to ID=0x{cmd_id:X} with payload={payload.hex()}")
    except Exception as e:
        print(f"[CAN_CLIENT] Error sending frame to ID=0x{cmd_id:X}: {e}")

def is_socket_valid(sock):
    """
    Sprawdza, czy socket jest poprawnie zainicjalizowany.
    """
    return sock is not None