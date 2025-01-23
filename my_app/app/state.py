from .models import DeviceAState, DeviceBState, ModuleCState

# Słownik: nazwa_bramki -> socket
bramki_sockets = {}

# Słownik: nazwa_urzadzenia (np. "A_bramka1") -> stan
devices_state = {
    "A_bramka1": DeviceAState(),
    "B_bramka1": DeviceBState(),
    "B_bramka2": DeviceBState()
}

# Stan modułu C (globalny)
module_c_state = ModuleCState()

# "globalny" socket do połączenia z emulatorem
client_socket = None