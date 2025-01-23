from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from can_gateway.can_client import send_command_to_b
from .. import state  # zawiera state.client_socket

router = APIRouter()

class DeviceBCommand(BaseModel):
    command: str
    value: Optional[int] = None

@router.get("/device-b/{bramka_name}/state")
def get_device_b_state(bramka_name: str):
    key = f"B_{bramka_name}"
    if key not in state.devices_state:
        return {"error": f"Device B not found for {bramka_name}"}
    return state.devices_state[key]

@router.post("/device-b/command")
def device_b_command(cmd: DeviceBCommand):
    sock = state.client_socket  # odwołanie do globalnego socketu
    if not sock:
        return {"status": "error", "msg": "No socket available"}

    if cmd.command == "reset_watchdog":
        # np. payload: [0x01]
        payload = bytes([0x01])
        send_command_to_b(sock, 0x200, payload)
        return {"status": "ok", "command_sent": "reset_watchdog"}

    elif cmd.command == "set_register" and cmd.value is not None:
        payload = bytearray(3)
        payload[0] = 0x02
        payload[1:3] = cmd.value.to_bytes(2, 'big')
        send_command_to_b(sock, 0x200, payload)
        return {"status": "ok", "command_sent": "set_register", "value": cmd.value}

    else:
        return {"status": "error", "msg": "Unknown command or missing value"}

@router.post("/device-b/{bramka_name}/command")
def device_b_command(bramka_name: str, cmd: DeviceBCommand):
    # Znajdź socket w state.bramki_sockets
    sock = state.bramki_sockets.get(bramka_name)
    if not sock:
        return {"status": "error", "msg": f"Bramka {bramka_name} not found"}

    if cmd.command == "reset_watchdog":
        payload = bytes([0x01])
        send_command_to_b(sock, 0x200, payload)
        return {"status": "ok", "command": cmd.command}