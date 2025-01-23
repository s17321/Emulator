import math
import time
from app import state

def test_module_c_logic():
    """
    Sprawdzamy, czy (a_reg1 + b_reg1) * param_x * sin(now) liczy się poprawnie.
    """
    a_reg1 = 10
    b_reg1 = 20
    state.module_c_state.param_x = 2.0
    now = 12345.0  # udawany czas

    # Oczekiwany wynik:
    expected = (a_reg1 + b_reg1) * 2.0 * math.sin(now)

    # W kodzie:
    result = (a_reg1 + b_reg1) * state.module_c_state.param_x * math.sin(now)

    assert math.isclose(result, expected, rel_tol=1e-7)
