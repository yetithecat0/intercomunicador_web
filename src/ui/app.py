import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN DE RUTAS Y CONSTANTES
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))
DIRECTORIO_CSV = os.path.join(PROJECT_ROOT, 'data', 'directorio.csv')
EVENTS_CSV = os.path.join(PROJECT_ROOT, 'data', 'registro_eventos.csv')

# Configuración de página
st.set_page_config(
    page_title="Res. Esmeralda Intercom 2026", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. ESTÉTICA CYBERPUNK (CSS NEÓN)
# ==========================================
st.markdown("""
<style>
    /* Fondo oscuro base */
    .stApp { 
        background-color: #0d0221; 
        color: #00fbff; 
    }
    
    /* Header Neón */
    .main-header {
        font-size: 2.2rem;
        font-weight: 900;
        color: #00fbff;
        text-align: center;
        text-shadow: 0 0 10px #00fbff, 0 0 20px #00fbff;
        letter-spacing: 3px;
        padding: 20px 0;
        border-bottom: 2px solid #ff00ff;
        margin-bottom: 30px;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Subtítulos y Radio Buttons */
    .stMarkdown p, .stRadio label {
        color: #00fbff !important;
        font-family: 'Courier New', Courier, monospace;
    }

    /* Botones de Navegación/Acción General (Cian) */
    div.stButton > button {
        background-color: transparent;
        color: #00fbff;
        border: 2px solid #00fbff;
        border-radius: 8px;
        padding: 15px;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(0, 251, 255, 0.2);
        transition: all 0.3s ease;
        text-transform: uppercase;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #00fbff;
        color: #0d0221;
        box-shadow: 0 0 20px #00fbff;
    }

    /* Botones de ACCIÓN (Verde Neón) - Call, Package, Visit */
    .action-btn button {
        background-color: transparent !important;
        color: #00ff41 !important;
        border: 2px solid #00ff41 !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2) !important;
    }

    .action-btn button:hover {
        background-color: #00ff41 !important;
        color: #0d0221 !important;
        box-shadow: 0 0 25px #00ff41 !important;
    }

    /* Botones de VOLVER / ERRORES (Magenta) */
    .back-btn button {
        border-color: #ff00ff !important;
        color: #ff00ff !important;
        box-shadow: 0 0 10px rgba(255, 0, 255, 0.2) !important;
    }

    .back-btn button:hover {
        background-color: #ff00ff !important;
        color: #0d0221 !important;
        box-shadow: 0 0 25px #ff00ff !important;
    }

    /* Estilo para Mensajes de Error y Warning (Magenta) */
    .stAlert {
        background-color: rgba(255, 0, 255, 0.1) !important;
        color: #ff00ff !important;
        border: 1px solid #ff00ff !important;
        border-radius: 10px !important;
    }
    .stAlert p {
        color: #ff00ff !important;
    }

    /* Auditoría Button (Especial) */
    .audit-btn button {
        border-style: dashed !important;
        font-size: 0.8rem !important;
        opacity: 0.8;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #ff00ff;
        box-shadow: 0 0 10px #ff00ff;
    }

    /* Inputs y Selectors */
    .stSelectbox, .stRadio, .stDataFrame {
        background: rgba(0, 251, 255, 0.05) !important;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(0, 251, 255, 0.3) !important;
    }

    /* Tarjeta Blanca de Alta Visibilidad (Pantalla 4) */
    .white-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(0, 251, 255, 0.3);
        border: none;
    }

    .white-card h2 {
        color: #1e293b !important;
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
        font-family: sans-serif !important;
    }

    .white-card .location-text {
        color: #64748b !important;
        font-size: 1.1rem !important;
        margin-bottom: 15px !important;
        font-family: sans-serif !important;
    }

    .white-card .resident-name {
        color: #003366 !important;
        font-size: 2.2rem !important;
        font-weight: 900 !important;
        margin: 15px 0 5px 0 !important;
        display: block !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    .white-card .resident-type-label {
        color: #64748b !important;
        font-size: 0.9rem !important;
        font-style: italic !important;
        margin-top: 0 !important;
        font-family: sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS Y EVENTOS
# ==========================================

@st.cache_data
def load_data():
    if not os.path.exists(DIRECTORIO_CSV):
        st.error("Error FATAL: Directorio no encontrado.")
        return pd.DataFrame()
    return pd.read_csv(DIRECTORIO_CSV, dtype={
        'telefono_prop': str, 
        'telefono_inq': str, 
        'departamento': str, 
        'piso': int
    })

def log_event(torre, departamento, tipo_accion):
    try:
        os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)
        file_exists = os.path.exists(EVENTS_CSV)
        now = datetime.now()
        event_row = {
            'fecha': now.strftime("%Y-%m-%d"),
            'hora': now.strftime("%H:%M:%S"),
            'torre': torre,
            'departamento': departamento,
            'tipo_accion': tipo_accion
        }
        with open(EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['fecha', 'hora', 'torre', 'departamento', 'tipo_accion'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(event_row)
    except Exception as e:
        st.error(f"Error de registro: {e}")

def open_whatsapp_js(phone, message=""):
    import urllib.parse
    encoded_msg = urllib.parse.quote(message)
    url = f"https://wa.me/{phone.replace('+', '')}?text={encoded_msg}"
    
    js = f"""
    <script>
        var win = window.open("{url}", "_blank");
        if(!win || win.closed || typeof win.closed=='undefined') {{ 
            alert("Bloqueador de ventanas activado. Por favor, permite popups para Esmeralda 2026."); 
        }}
        setTimeout(function() {{
            window.parent.document.dispatchEvent(new Event('keydown'));
        }}, 500);
    </script>
    """
    st.session_state.completado = True
    components.html(js, height=0)

# ==========================================
# 4. FLUJO DE APLICACIÓN
# ==========================================

# Inicialización de estado
if 'step' not in st.session_state: st.session_state.step = 1
df = load_data()

# Header común
st.markdown('<div class="main-header">RES. ESMERALDA 2026</div>', unsafe_allow_html=True)

# Barra de progreso (Cyberpunk Magenta)
st.progress(st.session_state.step / 4)

# --- PANTALLA 1: TORRE ---
if st.session_state.step == 1:
    st.markdown("<h3 style='text-align: center; color: #00fbff;'>🛸 SELECCIONE TORRE</h3>", unsafe_allow_html=True)
    
    torres = sorted(df['torre'].unique()) if not df.empty else ['T1', 'T2', 'T3']
    
    # Diseño de botones centrados y más extendidos (80% del ancho)
    for t in torres:
        col_side_alt1, col_center_alt1, col_side_alt2 = st.columns([0.1, 0.8, 0.1])
        with col_center_alt1:
            if st.button(f"TORRE {t[-1] if len(t)>1 else t}", key=f"btn_{t}"):
                st.session_state.sel_torre = t
                st.session_state.step = 2
                st.rerun()
    
    st.divider()
    col_side_alt3, col_center_alt3, col_side_alt4 = st.columns([0.2, 0.6, 0.2])
    with col_center_alt3:
        st.markdown('<div class="audit-btn">', unsafe_allow_html=True)
        if st.button("📊 AUDITORÍA DE EVENTOS (HOY)"):
            st.session_state.show_audit = True
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get('show_audit'):
        st.info(f"Historial del Día: {datetime.now().strftime('%Y-%m-%d')}")
        if os.path.exists(EVENTS_CSV):
            events_df = pd.read_csv(EVENTS_CSV)
            today = datetime.now().strftime('%Y-%m-%d')
            today_events = events_df[events_df['fecha'] == today].sort_values(by='hora', ascending=False)
            if not today_events.empty:
                st.dataframe(today_events[['hora', 'torre', 'departamento', 'tipo_accion']], use_container_width=True, hide_index=True)
            else:
                st.write("Sin actividad registrada hoy.")
        else:
            st.write("No existe archivo de registro aún.")
        if st.button("Cerrar Auditoría"):
            st.session_state.show_audit = False
            st.rerun()

# --- PANTALLA 2: PISO ---
elif st.session_state.step == 2:
    st.write(f"### 🧬 TORRE {st.session_state.sel_torre[-1]} > PISO")
    
    # Filtrar pisos disponibles para la torre
    pisos_disponibles = sorted(df[df['torre'] == st.session_state.sel_torre]['piso'].unique())
    
    # Grilla de 3 columnas
    for i in range(0, len(pisos_disponibles), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(pisos_disponibles):
                piso = pisos_disponibles[i + j]
                with cols[j]:
                    if st.button(f"PISO {piso}", key=f"p_{piso}"):
                        st.session_state.sel_piso = int(piso)
                        st.session_state.step = 3
                        st.rerun()
    
    st.write("")
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ VOLVER A TORRES"):
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 3: DEPARTAMENTO ---
elif st.session_state.step == 3:
    st.write(f"### 🏘️ TORRE {st.session_state.sel_torre[-1]} > PISO {st.session_state.sel_piso}")
    
    depts = df[(df['torre'] == st.session_state.sel_torre) & (df['piso'] == st.session_state.sel_piso)]
    
    if depts.empty:
        st.warning("No hay departamentos en este sector.")
    else:
        # Grilla de 2 columnas para depts (mejor legibilidad táctil)
        cols = st.columns(2)
        for i, row in enumerate(depts.itertuples()):
            with cols[i % 2]:
                if st.button(f"DEP. {row.departamento}", key=f"d_{row.departamento}"):
                    st.session_state.sel_dept_data = row
                    st.session_state.step = 4
                    st.rerun()

    st.write("")
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("⬅️ VOLVER A PISOS"):
        st.session_state.step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA 4: ACCIÓN ---
elif st.session_state.step == 4:
    row = st.session_state.sel_dept_data
    
    if st.session_state.get('completado'):
        st.success("⚡ PROTOCOLO INICIADO")
        if st.button("🔄 REINICIAR SISTEMA", type="primary"):
            st.session_state.step = 1
            st.session_state.completado = False
            st.rerun()
    else:
        # 1. Selector de Sujeto (Capa exterior)
        sujeto = st.radio("🔘 SELECCIONAR DESTINATARIO:", ["Propietario", "Inquilino"], horizontal=True)
        nombre_sujeto = row.propietario if sujeto == "Propietario" else row.inquilino
        telefono_destino = row.telefono_prop if sujeto == "Propietario" else row.telefono_inq
        
        # 2. Contenedor de Información (Tarjeta Blanca)
        st.markdown(f"""
        <div class="white-card">
            <h2>Departamento {row.departamento}</h2>
            <div class="location-text">Torre {st.session_state.sel_torre[-1]} | Piso {st.session_state.sel_piso}</div>
            <div class="resident-name">{nombre_sujeto}</div>
            <div class="resident-type-label">(Residente actual: {sujeto})</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Botones de Acción
        st.markdown('<div class="action-btn">', unsafe_allow_html=True)
        
        # Validación de Teléfono
        if telefono_destino == "---" or pd.isna(telefono_destino):
            st.warning(f"⚠️ No hay teléfono registrado para el {sujeto}.")
        else:
            # Botón LLAMAR (Verde Vibrante - Ancho Completo)
            if st.button("📞 LLAMAR POR WHATSAPP", use_container_width=True):
                log_event(st.session_state.sel_torre, row.departamento, f"Llamada ({sujeto})")
                open_whatsapp_js(telefono_destino, f"Hola {nombre_sujeto}, le saludamos de Vigilancia...")
                
            # Botones Secundarios (Horizontales)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📦 PAQUETE", use_container_width=True):
                    msg = "Estimado vecino, le saludamos de Vigilancia. Le informamos que tiene un paquete recibido en portería. Puede pasar a recogerlo cuando guste. Saludos."
                    log_event(st.session_state.sel_torre, row.departamento, f"Paquete ({sujeto})")
                    open_whatsapp_js(telefono_destino, msg)
            
            with col2:
                if st.button("👤 VISITA", use_container_width=True):
                    msg = "Buen día, le informamos que tiene una visita esperando por usted en la caseta de vigilancia. ¿Nos autoriza el ingreso? Quedamos atentos."
                    log_event(st.session_state.sel_torre, row.departamento, f"Visita ({sujeto})")
                    open_whatsapp_js(telefono_destino, msg)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 4. Botón de Retorno (Discreto)
        st.write("")
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ CAMBIAR DEPARTAMENTO"):
            st.session_state.step = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
