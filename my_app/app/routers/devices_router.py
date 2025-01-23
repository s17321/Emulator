from fastapi import APIRouter
from .. import state

router = APIRouter()

@router.get("/devices/{device_key}/state")
def get_device_state(device_key: str):
    """
    device_key może być np. "A_bramka1" albo "B_bramka2".
    Zwraca stan z state.devices_state[device_key].
    """
    if device_key not in state.devices_state:
        return {"error": "Unknown device_key"}
    return state.devices_state[device_key]