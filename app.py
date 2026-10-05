import streamlit as st

# Configuración de la página (opcional, para activar el modo oscuro por defecto si se desea)
st.set_page_config(layout="wide")

# Inyección de estilo Aero (Glassmorphism)
st.markdown(
    """
    <style>
    /* 1. Fondo principal de la aplicación: Un degradado dinámico azul/cian estilo Windows 7 */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #081b33 100%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

    /* 2. Efecto Vidrio Esmerilado (Glassmorphism) para los contenedores y tarjetas */
    div[data-testid="stVerticalBlock"] > div[dir="ltr"] > div {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 20px;
        margin-bottom: 15px;
    }

    /* 3. Estilo para los botones: Bordes redondeados y reflejo brillante al pasar el cursor */
    .stButton>button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        box-shadow: 0 0 15px rgba(0, 180, 255, 0.5), inset 0 1px 0 rgba(255,255,255,0.6);
        transform: translateY(-1px);
    }

    /* 4. Inputs y cajas de texto */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
    }

    /* 5. Asegurar que los textos sean legibles en blanco */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- EJEMPLO DE CONTENIDO CON ESTILO AERO ---
st.title("Windows Aero Interface")
st.write("Esta aplicación utiliza CSS inyectado para replicar el efecto de vidrio esmerilado.")

# Organizamos en columnas para ver cómo se estructuran las "tarjetas de vidrio"
col1, col2 = st.columns(2)

with col1:
    st.subheader("Controles Básicos")
    nombre = st.text_input("Introduce tu nombre:", "Usuario Aero")
    boton = st.button("Hacer clic aquí")

with col2:
    st.subheader("Estadísticas")
    st.metric(label="Rendimiento del Sistema", value="98.4 %", delta="Opc. Óptima")
    st.write(f"¡Hola {nombre}! El efecto de desenfoque se adapta al fondo de la pantalla.")