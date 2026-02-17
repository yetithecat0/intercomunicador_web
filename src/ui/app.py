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
# Configuración de página con el nuevo nombre
st.set_page_config(
    page_title="Res. Esmeralda Intercom 2026", 
    page_icon="💎", 
    layout="centered"
)

# Inyección de CSS Cyberpunk
st.markdown("""
    <style>
    /* Fondo oscuro futurista */
    .stApp { 
        background-color: #0d0221; 
        color: #00ff41; 
    }
    
    .main-header {
        font-size: 32px;
        font-weight: 900;
        color: #00fbff;
        text-align: center;
        text-shadow: 2px 2px 10px #00fbff;
        letter-spacing: 2px;
        margin-bottom: 20px;
        border-bottom: 2px solid #ff00ff;
    }

    /* Botones Generales (Estilo Neón) */
    div.stButton > button {
        background-color: #1a1a2e;
        color: #00fbff;
        border: 2px solid #00fbff;
        border-radius: 5px;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0 0 5px #00fbff;
        transition: all 0.3s;
    }

    div.stButton > button:hover {
        background-color: #00fbff;
        color: #1a1a2e;
        box-shadow: 0 0 20px #00fbff;
    }

    /* Botón LLAMAR (Verde Neón) */
    .stButton button[kind="primary"] {
        background: #00ff41 !important;
        color: #0d0221 !important;
        border: none !important;
        font-weight: bold !important;
        text-shadow: none !important;
        box-shadow: 0 0 15px #00ff41 !important;
    }

    /* Botón ATRÁS (Rojo/Magenta para diferenciar) */
    /* Usaremos una lógica de color para el botón que contenga "VOLVER" */
    div.stButton > button:contains("VOLVER"), 
    div.stButton > button:contains("CAMBIAR"),
    div.stButton > button:contains("CANCELAR") {
        border-color: #ff0055 !important;
        color: #ff0055 !important;
        box-shadow: 0 0 5px #ff0055 !important;
    }
    
    div.stButton > button:contains("VOLVER"):hover {
        background-color: #ff0055 !important;
        color: white !important;
    }

    /* Barra de progreso */
    .stProgress > div > div > div > div {
        background-color: #ff00ff;
    }
    </style>
    """, unsafe_allow_html=True)

# Actualizar el Header
st.markdown('<div class="main-header">💎 RES. ESMERALDA 2026</div>', unsafe_allow_html=True)

# ==========================================
# 2. FUNCIONES DE LÓGICA (Definir antes de usar)
# ==========================================

def open_whatsapp_and_mark_done(url):
    """Lanza WhatsApp con prioridad y luego actualiza la UI."""
    js = f"""
        <script>
            // Abrir WhatsApp primero
            var win = window.open("{url}", "_blank");
            
            // Si el navegador lo bloquea, avisar al usuario
            if(!win || win.closed || typeof win.closed=='undefined') {{ 
                alert("Por favor, permite los pop-ups para esta aplicación."); 
            }}
            
            // Esperar un instante y forzar el refresco de Streamlit
            setTimeout(function() {{
                window.parent.document.dispatchEvent(new Event('keydown'));
            }}, 300);
        </script>
    """
    st.session_state.completado = True
    components.html(js, height=0)

def log_event(torre, departamento, action):
    """Registra eventos en el archivo CSV de auditoría."""
    try:
        os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
        file_exists = os.path.exists(EVENTS_CSV)
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['fecha', 'hora', 'torre', 'departamento', 'tipo_accion'])
            now = datetime.now()
            writer.writerow([now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), torre, departamento, action])
    except Exception as e:
        st.error(f"Error al registrar evento: {e}")

@st.cache_data
def load_data():
    """Carga segura de base de datos local."""
    if not os.path.exists(DIRECTORIO_CSV):
        st.error("Error: Base de datos no encontrada.")
        return pd.DataFrame()
    return pd.read_csv(DIRECTORIO_CSV, dtype={'telefono': str, 'departamento': str})

# ==========================================
# 3. FLUJO DE PANTALLAS (CON NAVEGACIÓN DE RETORNO)
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
df = load_data()

st.markdown('<div class="main-header">🏢 INTERCOM PRO</div>', unsafe_allow_html=True)
st.progress(st.session_state.step / 4)

# --- PANTALLA 1: TORRES ---
if st.session_state.step == 1:
    st.markdown("<p style='text-align:center; color:#64748b;'>Seleccione la ubicación</p>", unsafe_allow_html=True)
    towers = ['T1', 'T2', 'T3']
    cols_t = st.columns(3)
    for idx, t in enumerate(towers):
        with cols_t[idx]:
            if st.button(f"TORRE {t[-1]}", key=f"t_{t}", use_container_width=True):
                st.session_state.selected_tower, st.session_state.step = t, 2
                st.rerun()

# --- PANTALLA 2: PISOS (CON BOTÓN ATRÁS) ---
elif st.session_state.step == 2:
    st.markdown(f"<p style='text-align:center;'><b>Torre {st.session_state.selected_tower[-1]}</b> > Seleccione Piso</p>", unsafe_allow_html=True)
    
    total_pisos = 16 
    for row_idx in range(0, total_pisos, 3):
        cols_p = st.columns(3)
        for col_idx in range(3):
            piso_num = row_idx + col_idx + 1
            if piso_num <= total_pisos:
                with cols_p[col_idx]:
                    if st.button(f"Piso {piso_num}", key=f"p_{piso_num}", use_container_width=True):
                        st.session_state.selected_floor, st.session_state.step = piso_num, 3
                        st.rerun()
    
    st.write("---")
    if st.button("⬅️ VOLVER A SELECCIÓN DE TORRE", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

# --- PANTALLA 3: DEPARTAMENTOS (CON BOTÓN ATRÁS) ---
elif st.session_state.step == 3:
    st.markdown(f"<p style='text-align:center;'><b>Torre {st.session_state.selected_tower[-1]} / Piso {st.session_state.selected_floor}</b></p>", unsafe_allow_html=True)
    filtered = df[(df['torre'] == st.session_state.selected_tower) & (df['piso'] == st.session_state.selected_floor)]
    
    if filtered.empty:
        st.warning("No hay departamentos registrados en este piso.")
    else:
        cols_d = st.columns(2)
        for i, row in enumerate(filtered.itertuples()):
            with cols_d[i%2]:
                if st.button(f"🏠 {row.departamento}", key=f"d_{row.departamento}", use_container_width=True):
                    st.session_state.selected_dept = row.departamento
                    st.session_state.phone = row.telefono
                    st.session_state.step = 4
                    st.rerun()
    
    st.write("---")
    if st.button("⬅️ VOLVER A SELECCIÓN DE PISO", use_container_width=True):
        st.session_state.step = 2
        st.rerun()

# --- PANTALLA 4: FICHA DE ACCIÓN (CON BOTÓN ATRÁS) ---
elif st.session_state.step == 4:
    if st.session_state.get('completado'):
        st.success("✅ ¡Proceso Iniciado!")
        if st.button("🔄 INICIAR NUEVA CONSULTA", type="primary", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    else:
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #e2e8f0;">
                <h2 style="color: #1e293b; margin:0;">Departamento {st.session_state.selected_dept}</h2>
                <p style="color: #64748b; font-size: 14px;">Torre {st.session_state.selected_tower[-1]} - Piso {st.session_state.selected_floor}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("📞 LLAMAR POR WHATSAPP", type="primary", use_container_width=True):
            log_event(st.session_state.selected_tower, st.session_state.selected_dept, "Llamada")
            url_ws = f"https://wa.me/{st.session_state.phone.replace('+', '')}"
            open_whatsapp_and_mark_done(url_ws)
            # <--- AQUÍ NO VA NADA MÁS. El JS hace el trabajo.

        if st.button("💬 MENSAJES RÁPIDOS", use_container_width=True):
            st.session_state.ver_mensajes = True
            st.rerun()

        # BOTONES DE MENSAJES RÁPIDOS
        if st.session_state.get('ver_mensajes'):
            st.divider()
            m1, m2 = st.columns(2)
            with m1:
                # MENSAJE DE PAQUETE
                msg_paquete = "Estimado vecino, le saludamos de Vigilancia. Le informamos que tiene un paquete recibido en portería. Puede pasar a recogerlo cuando guste. Saludos."
                if st.button("📦 Paquete"):
                    open_whatsapp_and_mark_done(f"https://wa.me/{st.session_state.phone}?text={msg_paquete}")
            
            with m2:
                # MENSAJE DE VISITA
                msg_visita = "Buen día, le informamos que tiene una visita esperando por usted en la caseta de vigilancia. ¿Nos autoriza el ingreso? Quedamos atentos."
                if st.button("👤 Visita"):
                    open_whatsapp_and_mark_done(f"https://wa.me/{st.session_state.phone}?text={msg_visita}")
        
        st.write("---")
        if st.button("⬅️ CAMBIAR DEPARTAMENTO", use_container_width=True):
            st.session_state.step = 3
            st.session_state.ver_mensajes = False
            st.rerun()
