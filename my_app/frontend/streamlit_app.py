# streamlit_app.py

import streamlit as st
import requests

# Możesz zmienić, jeśli Twoja aplikacja działa gdzie indziej:
API_BASE = "http://127.0.0.1:8000"

def main():
    st.title("Dashboard - Urządzenia A, B i Moduł C")

    st.subheader("Odczyt stanu urządzenia A")
    bramka_name_for_a = st.text_input("Nazwa bramki (np. bramka1) dla urządzenia A", "bramka1")
    if st.button("Pobierz stan A"):
        url_a = f"{API_BASE}/device-a/{bramka_name_for_a}/state"
        resp = requests.get(url_a)
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")

    st.subheader("Odczyt stanu urządzenia B")
    bramka_name_for_b = st.text_input("Nazwa bramki (np. bramka1) dla urządzenia B", "bramka1")
    if st.button("Pobierz stan B"):
        url_b = f"{API_BASE}/device-b/{bramka_name_for_b}/state"
        resp = requests.get(url_b)
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")

    st.subheader("Moduł C: stan i konfiguracja")
    # 1) Odczyt stanu
    if st.button("Pobierz stan Module C"):
        url_c_state = f"{API_BASE}/module-c/state"
        resp = requests.get(url_c_state)
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")

    # 2) Ustawianie param_x, param_y
    param_x_val = st.number_input("Param X", value=1.0)
    param_y_val = st.number_input("Param Y", value=2.0)
    if st.button("Ustaw parametry Module C"):
        url_c_config = f"{API_BASE}/module-c/config"
        payload = {"param_x": param_x_val, "param_y": param_y_val}
        resp = requests.post(url_c_config, json=payload)
        if resp.status_code == 200:
            st.success("Parametry zaktualizowane!")
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")


if __name__ == "__main__":
    main()
