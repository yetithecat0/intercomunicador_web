import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
import time

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
DIRECTORIO_CSV = os.path.join(DATA_DIR, 'directorio.csv')
EVENTS_CSV = os.path.join(DATA_DIR, 'registro_eventos.csv')
LOG_FILE = os.path.join(os.path.dirname(DATA_DIR), 'logs', 'intercom_history.log')

# Configure Logging
import logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True # Force reconfiguration on reload
)


# Configure page
st.set_page_config(page_title="Intercomunicador Web", page_icon="🏢", layout="centered")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_tower' not in st.session_state:
    st.session_state.selected_tower = None
if 'selected_floor' not in st.session_state:
    st.session_state.selected_floor = None
if 'selected_dept' not in st.session_state:
    st.session_state.selected_dept = None
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = None

# Load data
@st.cache_data
def load_data():
    if not os.path.exists(DIRECTORIO_CSV):
        st.error(f"Archivo de datos no encontrado: {DIRECTORIO_CSV}")
        return pd.DataFrame()
    return pd.read_csv(DIRECTORIO_CSV, dtype={'telefono': str, 'departamento': str})

df = load_data()

# Logic functions
def log_event(torre, depto, action):
    try:
        file_exists = os.path.exists(EVENTS_CSV)
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['fecha', 'hora', 'torre', 'departamento', 'tipo_accion'])
            
            now = datetime.now()
            writer.writerow([
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                torre,
                depto,
                action
            ])
        logging.info(f"Action logged: {action} to {torre}-{depto}")
        return True
    except Exception as e:
        logging.error(f"Error logging event: {e}")
        st.error(f"Error registrando evento: {e}")
        return False

def reset_app():
    st.session_state.step = 1
    st.session_state.selected_tower = None
    st.session_state.selected_floor = None
    st.session_state.selected_dept = None
    st.session_state.phone_number = None

# UI Styles
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .big-font {
        font-size: 24px !important;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 Intercomunicador Web")
if st.session_state.step == 1 and st.session_state.selected_tower is None:
    logging.info("Session started / Returned to Home")


# Step 1: Select Tower
if st.session_state.step == 1:
    st.markdown("### Seleccione la Torre")
    cols = st.columns(3)
    towers = ['T1', 'T2', 'T3']
    for i, tower in enumerate(towers):
        with cols[i]:
            if st.button(f"Torre {tower[-1]}", key=f"btn_{tower}"):
                st.session_state.selected_tower = tower
                logging.info(f"Selected Tower: {tower}")
                st.session_state.step = 2
                st.rerun()

# Step 2: Select Floor
elif st.session_state.step == 2:
    st.markdown(f"### Torre {st.session_state.selected_tower} - Seleccione el Piso")
    
    # Grid for 16 floors
    floors = list(range(1, 17))
    cols = st.columns(4)
    for i, floor in enumerate(floors):
        col_idx = i % 4
        with cols[col_idx]:
            if st.button(f"Piso {floor}", key=f"btn_piso_{floor}"):
                st.session_state.selected_floor = floor
                logging.info(f"Selected Floor: {floor}")
                st.session_state.step = 3
                st.rerun()
                
    st.markdown("---")
    if st.button("⬅️ Volver a Torres"):
        reset_app()
        st.rerun()

# Step 3: Select Apartment
elif st.session_state.step == 3:
    tower = st.session_state.selected_tower
    floor = st.session_state.selected_floor
    st.markdown(f"### {tower} - Piso {floor} - Seleccione Departamento")
    
    # Filter apartments for selected tower and floor
    # Assuming 'departamento' format includes floor (e.g., 101, 201) or is just an ID.
    # The prompt says "T1, T2, T3, 16 pisos, 4 deptos (101-104)".
    # Let's filter by 'piso' column from the CSV.
    
    filtered_df = df[(df['torre'] == tower) & (df['piso'] == floor)]
    
    if filtered_df.empty:
        st.warning("No se encontraron departamentos para este piso.")
    else:
        depts = filtered_df['departamento'].tolist()
        cols = st.columns(2)
        for i, dept in enumerate(depts):
            col_idx = i % 2
            with cols[col_idx]:
                if st.button(f"Depto {dept}", key=f"btn_dept_{dept}"):
                    st.session_state.selected_dept = dept
                    # Get phone number
                    phone = filtered_df[filtered_df['departamento'] == dept]['telefono'].values[0]
                    st.session_state.phone_number = phone
                    logging.info(f"Selected Dept: {dept} (Phone: {phone})")
                    st.session_state.step = 4
                    st.rerun()

    st.markdown("---")
    if st.button("⬅️ Volver a Pisos"):
        st.session_state.step = 2
        st.rerun()

# Step 4: Actions
elif st.session_state.step == 4:
    from src.logic.utils import open_whatsapp_popup

    dept = st.session_state.selected_dept
    phone = st.session_state.phone_number
    
    st.markdown(f"### Contactando Depto {dept}")
    st.info(f"📞 Número: {phone}")
    
    # State for message options
    if 'show_msg_options' not in st.session_state:
        st.session_state.show_msg_options = False
    
    col1, col2 = st.columns(2)
    
    # ----------------- BUTTON A: CALL -----------------
    with col1:
        # Action Button
        if st.button("📞 Realizar Llamada", type="primary"):
            log_event(st.session_state.selected_tower, dept, "Llamada")
            st.session_state.last_action_success = True
            wa_call_url = f"https://wa.me/{phone.replace('+', '')}"
            open_whatsapp_popup(wa_call_url)

    # ----------------- BUTTON B: MESSAGE -----------------
    with col2:
        if st.button("💬 Enviar Mensaje"):
            st.session_state.show_msg_options = True
            st.session_state.last_action_success = False # Reset success until actual msg sent

    # Message Options Area (below main buttons)
    if st.session_state.show_msg_options:
        st.write("---")
        st.markdown("##### Seleccione el mensaje:")
        m_col1, m_col2 = st.columns(2)
        
        msgs = ["Pedido en portería", "Visita esperando"]
        
        with m_col1:
            if st.button(msgs[0], key="msg_1"):
                log_event(st.session_state.selected_tower, dept, f"Mensaje: {msgs[0]}")
                st.session_state.last_action_success = True
                st.session_state.show_msg_options = False
                url = f"https://wa.me/{phone.replace('+', '')}?text={msgs[0].replace(' ', '%20')}"
                open_whatsapp_popup(url)

        with m_col2:
            if st.button(msgs[1], key="msg_2"):
                log_event(st.session_state.selected_tower, dept, f"Mensaje: {msgs[1]}")
                st.session_state.last_action_success = True
                st.session_state.show_msg_options = False
                url = f"https://wa.me/{phone.replace('+', '')}?text={msgs[1].replace(' ', '%20')}"
                open_whatsapp_popup(url)

    # Feedback Message
    if st.session_state.get('last_action_success'):
        st.success("✅ Solicitud atendida")

    # Navigation Buttons (Bottom / Sidebar)
    st.write("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col1:
        if st.button("⬅️ Volver", key="back_btn"):
            st.session_state.step = 3
            st.session_state.pop('last_action_success', None)
            st.session_state.pop('show_msg_options', None)
            st.rerun()
    with nav_col3:
        if st.button("🏠 Inicio", key="home_btn"):
            reset_app()
            st.session_state.pop('last_action_success', None)
            st.session_state.pop('show_msg_options', None)
            st.rerun()

