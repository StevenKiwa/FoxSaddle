
import streamlit as st

CIAN, MAGENTA, LIMA, VIOLETA = "#00f5ff", "#ff2bd6", "#b6ff3b", "#8a5cff"
FONDO, PANEL, GRILLA, TEXTO = "#0a0a12", "#12121f", "#1f1f33", "#e6e6f0"
ESCALA_NEON = [[0.0, "#1a0b3d"], [0.35, "#5b1fd1"], [0.7, MAGENTA], [1.0, CIAN]]   
ESCALA_LINEAS = [[0.0, VIOLETA], [0.5, MAGENTA], [1.0, CIAN]]                      
CELESTE_NEON = "#4AF7F3"   
OPACIDAD_3D = 0.30  
ETIQUETAS = [("x", MAGENTA), ("-x", MAGENTA), ("y", LIMA), ("-y", LIMA), ("z", CIAN), ("-z", CIAN)]


def aplicar_css():
    st.markdown(f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
      html, body, .stApp {{ font-family: 'Inter', sans-serif; }}
      .stApp {{ background: {FONDO}; color: {TEXTO}; }}
      [data-testid="stHeader"] {{ background: transparent; }}
      /* Elementos de la plataforma de alojamiento (menú, botón Deploy, icono de GitHub) que no se quieren mostrar.
         Solo afecta a lo que está DENTRO de la app; la insignia «Hosted with Streamlit» la dibuja Streamlit Community Cloud
         fuera de la app y no se puede ocultar desde aquí. */
      #MainMenu, footer, #GithubIcon, .stAppDeployButton, [data-testid="stDeployButton"], [data-testid="stToolbarActions"],
      [data-testid="stHeader"] a[href*="github.com"] {{ display: none !important; visibility: hidden !important; }}
      [data-testid="stSidebar"] {{ background: #0d0d18; border-right: 1px solid rgba(0,245,255,.18); }}
      h1, h2, h3 {{ color: {CIAN}; font-weight: 300; letter-spacing: 2px;
                    text-shadow: 0 0 14px rgba(0,245,255,.55); }}
      h4, h5 {{ color: {MAGENTA}; font-weight: 400; letter-spacing: 1px;
                text-shadow: 0 0 10px rgba(255,43,214,.45); }}
      hr {{ border-color: rgba(0,245,255,.15); }}
      .stButton > button {{ background: transparent; color: {CIAN}; border: 1px solid {CIAN};
          border-radius: 6px; box-shadow: 0 0 10px rgba(0,245,255,.35); transition: all .2s; }}
      .stButton > button:hover {{ background: rgba(0,245,255,.12); color: {CIAN}; border-color: {CIAN};
          box-shadow: 0 0 20px rgba(0,245,255,.85); }}
      [data-testid="stSidebar"] .stButton > button {{ width: 100%; }}
      .stTextInput input, .stNumberInput input {{ background: {PANEL}; color: {TEXTO};
          border: 1px solid #2a2a45; border-radius: 6px; }}
      .stTextInput input:focus, .stNumberInput input:focus {{ border-color: {MAGENTA};
          box-shadow: 0 0 10px rgba(255,43,214,.7); }}
      [data-testid="stAlert"] {{ background: rgba(18,18,31,.85); border: 1px solid rgba(0,245,255,.3);
          border-radius: 8px; color: {TEXTO}; }}
      [data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid rgba(182,255,59,.3);
          border-radius: 8px; padding: 12px 16px; }}
      [data-testid="stMetricValue"] {{ color: {LIMA}; text-shadow: 0 0 10px rgba(182,255,59,.6); }}
      [data-testid="stChatMessage"] {{ background: {PANEL}; border: 1px solid rgba(255,43,214,.25);
          border-radius: 10px; }}
      [data-testid="stChatInput"] {{ border: 1px solid rgba(0,245,255,.4); border-radius: 10px;
          box-shadow: 0 0 12px rgba(0,245,255,.2); }}
      [data-testid="stPlotlyChart"] {{ border: 1px solid rgba(0,245,255,.2); border-radius: 10px;
          box-shadow: 0 0 18px rgba(0,245,255,.12); overflow: hidden; }}
    </style>
    """, unsafe_allow_html=True)
