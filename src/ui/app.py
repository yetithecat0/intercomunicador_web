import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE RUTAS DINÁMICAS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Calculamos la raíz subiendo dos niveles desde src/ui/
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))
DIRECTORIO_CSV = os.path.join(PROJECT_ROOT, 'data', 'directorio.csv')
EVENTS_CSV = os.path.join(PROJECT_ROOT, 'data', 'registro_eventos.csv')

# 2. LÓGICA INTEGRADA (Ya no necesitas 'from src.logic.utils')
def open_whatsapp_popup(url):
    """Inyecta JavaScript para abrir WhatsApp en ventana emergente."""
    js = f"""<script>window.open("{url}", "_blank", "width=600,height=700");</script>"""
    components.html(js, height=0, width=0)

def log_event(torre, depto, action):
    """Registra eventos en el CSV de auditoría."""
    try:
        os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
        file_exists = os.path.exists(EVENTS_CSV)
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['fecha', 'hora', 'torre', 'departamento', 'tipo_accion'])
            now = datetime.now()
            writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), torre, depto, action])
        return True
    except Exception as e:
        st.error(f"Error al registrar: {e}")
        return False

# 3. INTERFAZ DE USUARIO
st.set_page_config(page_title="Intercomunicador Web", page_icon="🏢", layout="centered")

# Estilos visuales
st.markdown("""<style>
    .stButton>button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 10px; }
</style>""", unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 1

@st.cache_data
def load_data():
    if not os.path.exists(DIRECTORIO_CSV):
        st.error(f"No se encontró el archivo en: {DIRECTORIO_CSV}")
        return pd.DataFrame()
    return pd.read_csv(DIRECTORIO_CSV, dtype={'telefono': str, 'departamento': str})

df = load_data()

st.title("🏢 Intercomunicador Web")

# NAVEGACIÓN
if st.session_state.step == 1:
    st.subheader("Seleccione la Torre")
    cols = st.columns(3)
    for i, t in enumerate(['T1', 'T2', 'T3']):
        with cols[i]:
            if st.button(f"Torre {t[-1]}", key=f"t_{t}"):
                st.session_state.selected_tower, st.session_state.step = t, 2
                st.rerun()

elif st.session_state.step == 2:
    st.subheader(f"Torre {st.session_state.selected_tower} - Piso")
    cols = st.columns(4)
    for i in range(1, 17):
        with cols[(i-1)%4]:
            if st.button(f"Piso {i}", key=f"p_{i}"):
                st.session_state.selected_floor, st.session_state.step = i, 3
                st.rerun()
    if st.button("⬅️ Volver"): st.session_state.step = 1; st.rerun()

elif st.session_state.step == 3:
    st.subheader(f"Dpto en Piso {st.session_state.selected_floor}")
    f_df = df[(df['torre'] == st.session_state.selected_tower) & (df['piso'] == st.session_state.selected_floor)]
    cols = st.columns(2)
    for i, row in enumerate(f_df.itertuples()):
        with cols[i%2]:
            if st.button(f"Depto {row.departamento}", key=f"d_{row.departamento}"):
                st.session_state.selected_dept, st.session_state.phone = row.departamento, row.telefono
                st.session_state.step = 4
                st.rerun()
    if st.button("⬅️ Volver"): st.session_state.step = 2; st.rerun()

elif st.session_state.step == 4:
    st.subheader(f"Contactando Depto {st.session_state.selected_dept}")
    st.info(f"📞 Teléfono: {st.session_state.phone}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔴 LLAMAR", type="primary"):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Llamada")
            open_whatsapp_popup(f"https://wa.me/{st.session_state.phone.replace('+', '')}")
            st.success("✅ Solicitud atendida")
    with c2:
        if st.button("🔵 MENSAJE"):
            st.session_state.show_msg = True

    if st.session_state.get('show_msg'):
        m1, m2 = st.columns(2)
        if m1.button("Pedido en portería"):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Msg: Pedido")
            open_whatsapp_popup(f"https://wa.me/{st.session_state.phone}?text=Pedido%20en%20porteria")
            st.success("✅ Mensaje enviado")
        if m2.button("Visita esperando"):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Msg: Visita")
            open_whatsapp_popup(f"https://wa.me/{st.session_state.phone}?text=Visita%20esperando")
            st.success("✅ Mensaje enviado")

    if st.button("🏠 Inicio"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
