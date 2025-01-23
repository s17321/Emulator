import time
from emulator import emulator  # przykładowo, jeśli tak się nazywa Twój moduł

def test_watchdog_timeout():
    """
    Sprawdzamy, czy device_b_watchdog_ok staje się False
    po przekroczeniu WATCHDOG_TIMEOUT od ostatniego resetu.
    """
    emulator.device_b_watchdog_ok = True
    emulator.device_b_watchdog_timestamp = time.time() - emulator.WATCHDOG_TIMEOUT - 0.1
    # Symulujemy, że już minęło > WATCHDOG_TIMEOUT od ostatniego resetu

    # W realnym kodzie logika sprawdzania jest w handle_client_send
    # ale możemy wywołać bezpośrednio fragment, np.:
    emulator.check_watchdog_b()  # np. funkcja, która w oryginale jest w pętli

    assert emulator.device_b_watchdog_ok is False, "Watchdog powinien się wyłączyć"