from fastapi import APIRouter
from .. import state

router = APIRouter()

@router.get("/device-a/{bramka_name}/state")
def get_device_a_state(bramka_name: str):
    """
    Zwraca stan "A_{bramka_name}" z `devices_state`.
    """
    key = f"A_{bramka_name}"
    if key not in state.devices_state:
        return {"error": f"Device A not found for {bramka_name}"}
    return state.devices_state[key]