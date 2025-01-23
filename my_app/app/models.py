from pydantic import BaseModel
from typing import Dict

class DeviceAState(BaseModel):
    register_1: int = 0
    register_2: int = 0
    status: str = "OK"

class DeviceBState(BaseModel):
    register_1: int = 0
    register_2: int = 0
    watchdog_ok: bool = True

class ModuleCState(BaseModel):
    param_x: float = 1.0
    param_y: float = 2.0
    # Słownik wyników: nazwa_bramki -> float
    results: Dict[str, float] = {}

class ModuleCConfig(BaseModel):
    param_x: float
    param_y: float