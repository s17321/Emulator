from fastapi import APIRouter
from pydantic import BaseModel
from .. import state
module_c_state = state.module_c_state

router = APIRouter()

#odczyt aktualnego stanu modułu C
@router.get("/module-c/state")
def get_module_c_state():
    return state.module_c_state


# Dodatkowy model do aktualizacji parametrow modułu C
class ModuleCConfig(BaseModel):
    param_x: float
    param_y: float

#aktualizacja parametrów modułu C
@router.post("/module-c/config")
def update_module_c_config(config: ModuleCConfig):
    """
    Ustawia parametry param_x i param_y, w module_c_state używane do obliczeń w module C.
    """
    module_c_state.param_x = config.param_x
    module_c_state.param_y = config.param_y
    
    return {"status": "ok"}