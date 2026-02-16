import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y ESTILOS PRO
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))
DIRECTORIO_CSV = os.path.join(PROJECT_ROOT, 'data', 'directorio.csv')
EVENTS_CSV = os.path.join(PROJECT_ROOT, 'data', 'registro_eventos.csv')

# Configuración de página optimizada para móvil
st.set_page_config(
    page_title="INTERCOM PRO", 
    page_icon="🏢", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyección de CSS para estética Premium (Tarjetas y Sombras)
st.markdown("""
    <style>
    /* Fondo y contenedores */
    .stApp { background-color: #f8f9fa; }
    
    /* Títulos y Headers */
    .main-header {
        font-size: 28px;
        font-weight: 800;
        color: #1e293b;
        text-align: center;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    /* Estilo de Tarjetas (Cards) */
    div.stButton > button {
        background-color: white;
        color: #1e293b;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        height: 80px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
        transform: translateY(-2px);
    }

    div.stButton > button:active {
        transform: scale(0.95);
        background-color: #f1f5f9;
    }

    /* Botón de Acción Principal (Llamar) */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        color: white !important;
        border: none !important;
        height: 100px !important;
        font-size: 22px !important;
    }

    /* Botón de Mensaje */
    .stButton button[kind="secondary"] {
        background-color: #3b82f6 !important;
        color: white !important;
        height: 80px !important;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES NATIVAS
# ==========================================
def open_whatsapp_popup(url):
    """Lógica de apertura popup sin recargar app."""
    js = f"""<script>window.open("{url}", "_blank", "width=600,height=700");</script>"""
    components.html(js, height=0, width=0)

def log_event(torre, depto, action):
    """Auditoría de eventos en CSV."""
    try:
        os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
        file_exists = os.path.exists(EVENTS_CSV)
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['fecha', 'hora', 'torre', 'departamento', 'tipo_accion'])
            now = datetime.now()
            writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), torre, depto, action])
    except Exception as e:
        st.error(f"Error de registro: {e}")

@st.cache_data
def load_data():
    """Carga segura de base de datos local."""
    if not os.path.exists(DIRECTORIO_CSV):
        st.error("Error: Base de datos no encontrada.")
        return pd.DataFrame()
    return pd.read_csv(DIRECTORIO_CSV, dtype={'telefono': str, 'departamento': str})

# ==========================================
# 3. FLUJO DE PANTALLAS (UX PRO)
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
df = load_data()

# Header fijo con barra de progreso
st.markdown('<div class="main-header">🏢 INTERCOM PRO</div>', unsafe_allow_html=True)
st.progress(st.session_state.step / 4)

# --- PANTALLA 1: TORRES ---
if st.session_state.step == 1:
    st.markdown("<p style='text-align:center; color:#64748b;'>Seleccione la ubicación</p>", unsafe_allow_html=True)
    towers = ['T1', 'T2', 'T3']
    for t in towers:
        if st.button(f"TORRE {t[-1]}", key=f"t_{t}"):
            st.session_state.selected_tower, st.session_state.step = t, 2
            st.rerun()

# --- PANTALLA 2: PISOS ---
elif st.session_state.step == 2:
    st.markdown(f"<p style='text-align:center;'><b>Torre {st.session_state.selected_tower[-1]}</b> > Seleccione Piso</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i in range(1, 17):
        with cols[(i-1)%3]:
            if st.button(f"Piso {i}", key=f"p_{i}"):
                st.session_state.selected_floor, st.session_state.step = i, 3
                st.rerun()
    if st.button("⬅️ VOLVER", key="back_1"): st.session_state.step = 1; st.rerun()

# --- PANTALLA 3: DEPARTAMENTOS (GRILLA) ---
elif st.session_state.step == 3:
    st.markdown(f"<p style='text-align:center;'><b>Piso {st.session_state.selected_floor}</b> > Departamento</p>", unsafe_allow_html=True)
    filtered = df[(df['torre'] == st.session_state.selected_tower) & (df['piso'] == st.session_state.selected_floor)]
    
    if filtered.empty:
        st.warning("No hay datos para este piso.")
    else:
        cols = st.columns(2)
        for i, row in enumerate(filtered.itertuples()):
            with cols[i%2]:
                if st.button(f"🏠 {row.departamento}", key=f"d_{row.departamento}"):
                    st.session_state.selected_dept = row.departamento
                    st.session_state.phone = row.telefono
                    st.session_state.step = 4
                    st.rerun()
    if st.button("⬅️ VOLVER", key="back_2"): st.session_state.step = 2; st.rerun()

# --- PANTALLA 4: FICHA DE ACCIÓN ---
elif st.session_state.step == 4:
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 20px; text-align: center; border: 1px solid #e2e8f0; margin-bottom: 20px;">
            <p style="color: #64748b; font-size: 14px; margin-bottom: 0;">DEPARTAMENTO</p>
            <h1 style="color: #1e293b; margin-top: 0;">{st.session_state.selected_dept}</h1>
            <p style="color: #3b82f6; font-weight: bold;">📞 {st.session_state.phone}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("📞 LLAMAR AHORA", type="primary", use_container_width=True):
        log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Llamada")
        open_whatsapp_popup(f"https://wa.me/{st.session_state.phone.replace('+', '')}")
        st.success("Llamada iniciada")

    st.write(" ") # Espaciador
    
    if st.button("💬 ENVIAR MENSAJE", type="secondary", use_container_width=True):
        st.session_state.msg_active = True

    if st.session_state.get('msg_active'):
        st.divider()
        m1, m2 = st.columns(2)
        if m1.button("📦 Pedido"):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Msg: Pedido")
            open_whatsapp_popup(f"https://wa.me/{st.session_state.phone}?text=Tiene%20un%20pedido%20en%20porteria")
        if m2.button("👤 Visita"):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Msg: Visita")
            open_whatsapp_popup(f"https://wa.me/{st.session_state.phone}?text=Su%20visita%20ha%20llegado")

    st.write("---")
    if st.button("🏠 FINALIZAR Y VOLVER", key="home"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
