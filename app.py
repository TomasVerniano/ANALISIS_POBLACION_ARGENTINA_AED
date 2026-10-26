#librerias
import base64
import re
import unicodedata
import os
import altair as alt
import numpy as np
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st
from pathlib import Path

#ttulo
st.set_page_config(page_title="Dashboard de Natalidad", page_icon="🫃", layout="wide")

#paletas
BG, CARD, TEXT, MUTED = "#0F1B33", "#1A2B4A", "#EAF0FA", "#9FB0CC"
BLUE, TEAL, YELLOW, CORAL = "#3F7FC4", "#3BB8A6", "#F5B942", "#E8605F"

#declaracion d pestañas
if "ver_general" not in st.session_state:
  st.session_state.ver_general = False

if "ver_storytelling" not in st.session_state:
  st.session_state.ver_storytelling = False

if "ver_causas" not in st.session_state:
   st.session_state.ver_causas = False

#cargamos el df
@st.cache_data
def cargar_datos():
  df_madres = pd.read_csv(r"DATA_PROCESADA\POBLACION\nacimientos_provi_año.csv")
  mapeo_provincias = {
      "Cordoba": "Córdoba",
      "Entre Rios": "Entre Ríos",
      "Neuquen": "Neuquén",
      "Rio Negro": "Río Negro",
      "Tucuman": "Tucumán",
      "Tierra del Fuego": (
          "Tierra del Fuego"
      ),

    
  }
  df_madres["provincia"] = df_madres["provincia"].replace(mapeo_provincias)
  return df_madres

df_agrupado = cargar_datos()

#variables globales del storyletin
serie = df_agrupado.groupby("anio", as_index=False)["nacimientos"].sum().sort_values("anio").reset_index(drop=True)
serie["var_pct"] = serie["nacimientos"].pct_change() * 100
ANIOS = serie["anio"].tolist()
Y0, Y1 = ANIOS[0], ANIOS[-1]
N0 = int(serie.loc[serie.anio == Y0, "nacimientos"].iloc[0])
N1 = int(serie.loc[serie.anio == Y1, "nacimientos"].iloc[0])
fila_pico = serie.loc[serie["nacimientos"].idxmax()]
YP, NP = int(fila_pico["anio"]), int(fila_pico["nacimientos"])
CAIDA_PICO = (N1 / NP - 1) * 100
fila_peor = serie.loc[serie["var_pct"].idxmin()] if serie["var_pct"].notna().any() else None



#cargamos la figura del mapa de abajo
@st.cache_data
def cargar_geojson():
  url = "https://apis.datos.gob.ar/georef/api/v2.0/provincias.geojson"
  return requests.get(url).json()


geojson_arg = cargar_geojson()
nombres_provincias = [
    feature["properties"]["nombre"] for feature in geojson_arg["features"]
]



#temas de color
lista_temas_color = [
    "magma",
    "cividis",
    "greens",
    "inferno",
    "blues",
    "plasma",
    "reds",
    "rainbow",
    "turbo",
    "viridis",
]

PALETAS = ["Viridis", "Cividis", "Blues", "Greens", "Reds", "Inferno", "Magma", "Plasma", "Turbo"]
paleta = "Viridis"

FONDOS = {
    **{a: "pj.png" for a in (2012, 2013, 2014)},
    **{a: "pro.png" for a in (2015, 2016, 2017, 2018)},
    **{a: "fdt.png" for a in (2019, 2020, 2021, 2022, 2023)},
    2024: "lla.png",
}


#herramientas de formato
def fmt(n) -> str:
    return f"{n:,.0f}".replace(",", ".")

def fpct(n, dec=1, signo=False) -> str:
    s = f"{n:+.{dec}f}" if signo else f"{n:.{dec}f}"
    return s.replace(".", ",").replace("-", "−") + "%"

def sube_baja(a, b) -> str:
    return "bajaron" if b < a else "subieron"

def leer_csv(carpeta: str, archivo: str):
    ruta = Path("DATA_PROCESADA") / carpeta / archivo
    if not ruta.exists():
        return None
    try:
        df = pd.read_csv(ruta)
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, encoding="latin1")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def clave_prov(nombre) -> str:
    s = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().lower().strip()
    if s.startswith("tierra del fuego"):
        return "tierra del fuego"
    if "ciudad" in s or "caba" in s or "capital federal" in s:
        return "caba"
    return s

df_prov = leer_csv("POBLACION", "nacimientos_provi_año.csv")



#barra del costado
with st.sidebar:
  st.title("🇦🇷 Dashboard de Natalidad")

  # logica de la barra del costado
  if st.session_state.ver_storytelling:
    if st.button("⬅ Volver al Dashboard", use_container_width=True):
      st.session_state.ver_storytelling = False
      st.session_state.ver_general = False
      st.session_state.ver_causas = False
      st.rerun()
    anio_seleccionado = df_agrupado.anio.max()
    tema_color_seleccionado = "viridis"

  elif st.session_state.ver_general:
    if st.button("⬅ Volver al Dashboard", use_container_width=True):
      st.session_state.ver_general = False
      st.rerun()
    anio_seleccionado = df_agrupado.anio.max()
    
    tema_color_seleccionado = st.selectbox(
        "Seleccione un color", lista_temas_color
    )
    
    st.divider()
    if st.button("📖 Storytelling", use_container_width=True):
      st.session_state.ver_storytelling = True
      st.session_state.ver_general = False
      st.session_state.ver_causas = False
      st.rerun()

    if st.button("🚩 Contexto Politico", use_container_width=True):
      st.session_state.ver_storytelling = False
      st.session_state.ver_general = False
      st.session_state.ver_causas = True
      st.rerun()

  elif st.session_state.ver_causas:
    if st.button("⬅ Volver al Dashboard", use_container_width=True):
      st.session_state.ver_storytelling = False
      st.session_state.ver_general = False
      st.session_state.ver_causas = False
      st.rerun()
    anio_seleccionado = df_agrupado.anio.max()
    tema_color_seleccionado = "viridis"

    st.markdown("### 📉 Políticas y natalidad")
    st.markdown("""
        [1 · 2014 · Implante subdérmico](#h1)  
        [2 · 2015 · Autonomía progresiva](#h2)  
        [3 · 2017 · Plan ENIA](#h3)  
        [4 · 2020 · Ley 27.610](#h4)  
        [Cómo leer estos gráficos](#lectura)
            """)
    st.caption("Nacimientos según la edad de la madre. Fuente: Estadísticas Vitales (DEIS), datos.gob.ar.")

  else:
    if st.button("Ver Avance General", use_container_width=True):
      st.session_state.ver_general = True
      st.session_state.ver_storytelling = False
      st.session_state.ver_causas = False
      st.rerun()

    lista_anios = list(df_agrupado.anio.unique())[::-1]
    anio_seleccionado = st.selectbox("Seleccione un año", lista_anios)

    tema_color_seleccionado = st.selectbox(
        "Seleccione un color", lista_temas_color
    )

    st.divider()

    if st.button("📖 Storytelling", use_container_width=True):
      st.session_state.ver_storytelling = True
      st.session_state.ver_general = False
      st.session_state.ver_causas = False
      st.rerun()

    if st.button("🚩 Contexto Politico", use_container_width=True):
      st.session_state.ver_storytelling = False
      st.session_state.ver_general = False
      st.session_state.ver_causas = True
      st.rerun()

  # ocultar fondo
  usar_fondo = st.toggle(
      "🖼️ Fondo ilustrado por período",
      value=True,
      help="Muestra u oculta las imágenes de fondo según el año o la sección.",
  )

  df_anio_seleccionado = df_agrupado[df_agrupado.anio == anio_seleccionado]
  df_anio_ordenado = df_anio_seleccionado.sort_values(
      by="nacimientos", ascending=False
  )


#convertir imagen local a url
def get_base64_img(file_path):
  if not os.path.exists(file_path):
    return ""
  with open(file_path, "rb") as f:
    data = f.read()
  return base64.b64encode(data).decode()


base64_string = ""
if usar_fondo:
  if st.session_state.ver_storytelling or st.session_state.ver_general or st.session_state.ver_causas:
    ruta_local = os.path.join("BACKGROUNDS", "general.png")
  else:
    nombre_fondo = FONDOS.get(anio_seleccionado, "pj.png")
    ruta_local = os.path.join("BACKGROUNDS", nombre_fondo)

  base64_string = get_base64_img(ruta_local)

if usar_fondo and base64_string:
  background_style = (
      f'background-image: url("data:image/png;base64,{base64_string}");'
      "background-size: cover; background-position: center; background-attachment: fixed;"
  )
else:
  background_style = "background: #1e1e24;"


#diseño de la pag


custom_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
}}

[data-testid="block-container"] {{
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}}

[data-testid="stAppViewContainer"] {{
    {background_style}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: #EAF0FA !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

section[data-testid="stSidebar"] {{
    background: #0B1428 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}}

/* Contenedores Glassmorphic principales */
div[data-testid="stVerticalBlock"] > div[dir="ltr"] > div {{
    background: rgba(26, 43, 74, 0.65) !important;
    backdrop-filter: blur(14px) saturate(180%);
    -webkit-backdrop-filter: blur(14px) saturate(180%);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    padding: 20px;
    margin-bottom: 15px;
}}

/* Botones unificados */
.stButton>button {{
    background: rgba(255, 255, 255, 0.12) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(6px);
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}}

.stButton>button:hover {{
    background: rgba(59, 184, 166, 0.3) !important;
    border-color: #3BB8A6 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}}

/* Tarjetas HTML personalizadas */
.card {{
    background: rgba(26, 43, 74, 0.8);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-left: 5px solid #3BB8A6;
    backdrop-filter: blur(10px);
}}
.card.blue {{ border-left-color: #3F7FC4; }}
.card.yellow {{ border-left-color: #F5B942; }}
.card.coral {{ border-left-color: #E8605F; }}

.card h4 {{ margin: 0 0 8px 0; color: #ffffff; font-size: 1.1rem; font-weight: 700; }}
.card p, .card li {{ color: #EAF0FA; font-size: 0.95rem; line-height: 1.5; margin: 0; }}

/* Big Numbers / Métricas */
.bignum {{
    text-align: center;
    padding: 18px 10px;
    background: rgba(26, 43, 74, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    backdrop-filter: blur(10px);
}}
.bignum .n {{ font-size: 2.5rem; font-weight: 900; line-height: 1.05; }}
.bignum .l {{ color: #9FB0CC; margin-top: 6px; font-size: 0.88rem; line-height: 1.3; }}

/* Callouts y Encabezados */
.hero {{
    padding: 2.5rem 2rem;
    border-radius: 20px;
    margin-bottom: 25px;
    text-align: center;
    background: radial-gradient(circle at 85% 20%, rgba(29, 58, 107, 0.8) 0%, rgba(15, 27, 51, 0.9) 62%);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}}
.hero h1 {{ font-size: 2.8rem; font-weight: 900; color: #F5B942; margin-bottom: 10px; text-transform: uppercase; }}
.hero .sub {{ font-size: 1.2rem; color: #EAF0FA; font-style: italic; }}

.kicker {{ color: #3BB8A6; font-weight: 800; letter-spacing: .1em; font-size: 0.85rem; margin-top: 2rem; text-transform: uppercase; }}
.title {{ font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 0.3rem 0; }}
.rule {{ width: 60px; height: 4px; background: #3BB8A6; border-radius: 4px; margin: 0.5rem 0 1.2rem 0; }}

.callout {{
    background: linear-gradient(135deg, rgba(59,184,166,0.25), rgba(63,127,196,0.25));
    border-radius: 14px;
    padding: 18px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #F5B942;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.2);
    margin: 15px 0;
}}

.note {{ color: #9FB0CC; font-size: 0.88rem; font-style: italic; margin: 8px 0; }}
.src {{ color: #7e90b0; font-size: 0.8rem; margin-top: 5px; }}

h1, h2, h3, h4, h5, h6, p, label {{
    color: #ffffff !important;
}}
</style>
"""

st.html(custom_css)

st.html(custom_css)


# mapa d calor
def crear_mapa_calor(df_entrada, eje_y, eje_x, columna_color, esquema_color):
  mapa_calor = (
      alt.Chart(df_entrada)
      .mark_rect()
      .encode(
          y=alt.Y(f"{eje_y}:O", axis=alt.Axis(title="Año", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
          x=alt.X(f"{eje_x}:O", axis=alt.Axis(title="Provincia", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=-45)),
          color=alt.Color(f"max({columna_color}):Q", legend=None, scale=alt.Scale(scheme=esquema_color)),
          stroke=alt.value("black"),
          strokeWidth=alt.value(0.25),
      )
      .properties(width=900, height=400)
      .configure_axis(labelFontSize=11, titleFontSize=12)
  )
  return mapa_calor

#grafico barras
def crear_grafico_barras(df_entrada, eje_x, eje_y, esquema_color):
  grafico = px.bar(
      df_entrada,
      x=eje_x,
      y=eje_y,
      color=eje_x,
      color_discrete_sequence=px.colors.qualitative.Prism,
      template="plotly_dark",
  )
  grafico.update_layout(
      plot_bgcolor="rgba(0, 0, 0, 0)",
      paper_bgcolor="rgba(0, 0, 0, 0)",
      margin=dict(l=0, r=0, t=0, b=0),
      height=350,
      showlegend=False,
  )
  return grafico

#dona
def dona(valor, color, titulo, alto=210):
    f = go.Figure(go.Pie(values=[valor, max(100 - valor, 0)], hole=0.72, sort=False,
                         marker=dict(colors=[color, "#22345a"]), textinfo="none", hoverinfo="skip"))
    f.add_annotation(text=f"<b>{fpct(valor, 0)}</b>", x=0.5, y=0.5, showarrow=False,
                     font=dict(size=26, color=color))
    f.update_layout(title=dict(text=titulo, x=0.5, font=dict(size=14)))
    return estilo(f, alto)

def crear_grafico_dona(valor_porcentaje, texto_etiqueta, color_tema):
  if color_tema == "blue":
    colores_grafico = ["#29b5e8", "#155F7A"]
  elif color_tema == "green":
    colores_grafico = ["#27AE60", "#12783D"]
  elif color_tema == "orange":
    colores_grafico = ["#F39C12", "#875A12"]
  elif color_tema == "red":
    colores_grafico = ["#E74C3C", "#781F16"]
  else:
    colores_grafico = ["#29b5e8", "#155F7A"]

  fuente_datos = pd.DataFrame({"Tema": ["", texto_etiqueta], "% valor": [100 - valor_porcentaje, valor_porcentaje]})
  fuente_datos_fondo = pd.DataFrame({"Tema": ["", texto_etiqueta], "% valor": [100, 0]})

  grafico = alt.Chart(fuente_datos).mark_arc(innerRadius=45, cornerRadius=45).encode(
      theta="% valor",
      color=alt.Color("Tema:N", scale=alt.Scale(domain=[texto_etiqueta, ""], range=colores_grafico), legend=None),
  ).properties(width=130, height=130)

  texto = grafico.mark_text(align="center", color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f"{valor_porcentaje} %"))
  grafico_fondo = alt.Chart(fuente_datos_fondo).mark_arc(innerRadius=45, cornerRadius=20).encode(
      theta="% valor",
      color=alt.Color("Tema:N", scale=alt.Scale(domain=[texto_etiqueta, ""], range=colores_grafico), legend=None),
  ).properties(width=130, height=130)

  return ((grafico_fondo + grafico + texto).configure_view(fill="black").configure(background="transparent"))

#formato a los num
def formatear_numero(numero):
  if numero > 1000000:
    if not numero % 1000000:
      return f"{numero // 1000000} M"
    return f"{round(numero / 1000000, 1)} M"
  return f"{numero // 1000} K"


def calcular_diferencia_nacimientos(df_entrada, anio_consulta):
  datos_anio_actual = df_entrada[df_entrada["anio"] == anio_consulta].reset_index(drop=True)
  datos_anio_anterior = df_entrada[df_entrada["anio"] == anio_consulta - 1].reset_index(drop=True)

  if not datos_anio_anterior.empty:
    datos_anio_actual["diferencia_nacimientos"] = datos_anio_actual.nacimientos.sub(datos_anio_anterior.nacimientos, fill_value=0)
  else:
    datos_anio_actual["diferencia_nacimientos"] = 0

  return pd.concat([datos_anio_actual.provincia, datos_anio_actual.nacimientos, datos_anio_actual.diferencia_nacimientos], axis=1).sort_values(by="diferencia_nacimientos", ascending=False)


if not st.session_state.ver_general and not st.session_state.ver_storytelling and not st.session_state.ver_causas:
  columnas = st.columns((1.5, 4.5, 2), gap="medium")

  #columna0
  with columnas[0]:
    st.markdown("#### Variación Anual")

    anio_minimo = df_agrupado.anio.min()
    df_diferencia_ordenado = calcular_diferencia_nacimientos(
        df_agrupado, anio_seleccionado
    )

    if anio_seleccionado > anio_minimo:
      nombre_primera_provincia = df_diferencia_ordenado.provincia.iloc[0]
      nacimientos_primera_provincia = formatear_numero(
          df_diferencia_ordenado.nacimientos.iloc[0]
      )
      variacion_primera_provincia = formatear_numero(
          df_diferencia_ordenado.diferencia_nacimientos.iloc[0]
      )
    else:
      nombre_primera_provincia = "-"
      nacimientos_primera_provincia = "-"
      variacion_primera_provincia = ""
    st.metric(
        label=nombre_primera_provincia,
        value=nacimientos_primera_provincia,
        delta=variacion_primera_provincia,
    )

    if anio_seleccionado > anio_minimo:
      nombre_ultima_provincia = df_diferencia_ordenado.provincia.iloc[-1]
      nacimientos_ultima_provincia = formatear_numero(
          df_diferencia_ordenado.nacimientos.iloc[-1]
      )
      variacion_ultima_provincia = formatear_numero(
          df_diferencia_ordenado.diferencia_nacimientos.iloc[-1]
      )
    else:
      nombre_ultima_provincia = "-"
      nacimientos_ultima_provincia = "-"
      variacion_ultima_provincia = ""
    st.metric(
        label=nombre_ultima_provincia,
        value=nacimientos_ultima_provincia,
        delta=variacion_ultima_provincia,
    )

    st.markdown("#### Tendencia Provincial")

    if anio_seleccionado > anio_minimo:
      df_en_alza = df_diferencia_ordenado[
          df_diferencia_ordenado.diferencia_nacimientos > 0
      ]
      df_a_la_baja = df_diferencia_ordenado[
          df_diferencia_ordenado.diferencia_nacimientos < 0
      ]

      porcentaje_alza = round(
          (len(df_en_alza) / df_diferencia_ordenado.provincia.nunique()) * 100
      )
      porcentaje_baja = round(
          (len(df_a_la_baja) / df_diferencia_ordenado.provincia.nunique()) * 100
      )

      grafico_dona_alza = crear_grafico_dona(porcentaje_alza, "En Alza", "green")
      grafico_dona_baja = crear_grafico_dona(porcentaje_baja, "A la Baja", "red")
    else:
      grafico_dona_alza = crear_grafico_dona(0, "En Alza", "green")
      grafico_dona_baja = crear_grafico_dona(0, "A la Baja", "red")

    columnas_tendencia = st.columns((0.2, 1, 0.2))
    with columnas_tendencia[1]:
      st.write("En Alza")
      st.altair_chart(grafico_dona_alza)
      st.write("A la Baja")
      st.altair_chart(grafico_dona_baja)

  with columnas[1]:
    st.markdown("#### Total de Nacimientos por Provincia")

    grafico_barras = crear_grafico_barras(
        df_anio_ordenado, "provincia", "nacimientos", tema_color_seleccionado
    )
    st.plotly_chart(grafico_barras, use_container_width=True)

    st.markdown("#### Mapa de Calor Histórico")
    mapa_calor = crear_mapa_calor(
        df_agrupado, "anio", "provincia", "nacimientos", tema_color_seleccionado
    )
    st.altair_chart(mapa_calor, use_container_width=True)

  with columnas[2]:
    st.markdown("#### Top Provincias")

    st.dataframe(
        df_anio_ordenado,
        column_order=("provincia", "nacimientos"),
        hide_index=True,
        column_config={
            "provincia": st.column_config.TextColumn(
                "Provincia",
            ),
            "nacimientos": st.column_config.ProgressColumn(
                "Nacimientos",
                format="%d",
                min_value=0,
                max_value=int(max(df_anio_ordenado.nacimientos)),
            ),
        },
    )

    with st.expander("Acerca de", expanded=True):
      st.write("""
            - Datos: Estadísticas Vitales - Argentina.
            - :orange[**Variación Anual**]: Provincias con mayor aumento/disminución de nacimientos respecto al año previo.
            - :orange[**Tendencia Provincial**]: Porcentaje de provincias con variaciones positivas o negativas.
            """)

  st.markdown(f"🇦🇷 Mapa Coroplético de Argentina ({anio_seleccionado})")

  df_base_mapa = pd.DataFrame({"provincia": nombres_provincias})
  df_mapa_final = pd.merge(
      df_base_mapa,
      df_anio_seleccionado[["provincia", "nacimientos"]],
      on="provincia",
      how="left",
  )
  df_mapa_final["nacimientos"] = df_mapa_final["nacimientos"].fillna(0)

  col_mapa_izq, col_mapa_centro, col_mapa_der = st.columns([1, 2, 1])

  #el resto del mapa
  with col_mapa_centro:
    fig = px.choropleth(
        df_mapa_final,
        geojson=geojson_arg,
        locations="provincia",
        featureidkey="properties.nombre",
        color="nacimientos",
        color_continuous_scale=tema_color_seleccionado,
        range_color=[
            df_mapa_final["nacimientos"].min(),
            df_mapa_final["nacimientos"].max(),
        ],
        labels={"nacimientos": "Nacimientos"},
        hover_name="provincia",
    )

    fig.update_geos(
        lataxis_range=[-57.0, -21.0],
        lonaxis_range=[-74.5, -52.5],
        visible=False,

        bgcolor="rgba(0,0,0,0)"
    )

    fig.update_layout(
        height=800,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        

        coloraxis_colorbar=dict(
            title="Intensidad",
            thickness=20,
            len=0.6,
            x=0.9,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


#caracteristicas de la pestaña d las contexto politico
BASE = Path(__file__).resolve().parent
PROC = BASE / "DATA_PROCESADA"

@st.cache_data
def leer_csv(carpeta: str, archivo: str):
    ruta = PROC / carpeta / archivo
    if not ruta.exists():
        return None
    df = pd.read_csv(ruta)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def inicio_edad(txt):
    m = re.search(r"\d+", str(txt))
    return int(m.group()) if m else None


def clave_prov(nombre) -> str:
    s = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().lower().strip()
    if s.startswith("tierra del fuego"):
        return "tierra del fuego"
    if "ciudad" in s or "caba" in s or "capital federal" in s:
        return "caba"
    return s


df_m = leer_csv("POBLACION", "madres_grupo_edad_total.csv")
if df_m is None or not {"anio", "grupo_etario_madre", "cantidad"} <= set(df_m.columns):
    st.error("Falta `DATA_PROCESADA/POBLACION/madres_grupo_edad_total.csv` (se genera en poblacion.ipynb).")
    st.stop()

df_m = df_m.copy()
df_m["anio"] = df_m["anio"].astype(int)
df_m["ini"] = df_m["grupo_etario_madre"].map(inicio_edad)

por_anio = lambda mask: df_m[mask].groupby("anio")["cantidad"].sum().sort_index()
S = pd.DataFrame({
    "10-14": por_anio(df_m["ini"] < 15),
    "15-19": por_anio((df_m["ini"] >= 15) & (df_m["ini"] < 20)),
    "<20": por_anio(df_m["ini"] < 20),
    "20+": por_anio(df_m["ini"] >= 20),
})
df_tot = leer_csv("POBLACION", "nacimientos_total_año.csv")
if df_tot is not None and {"anio", "nacimientos"} <= set(df_tot.columns):
    S["total"] = df_tot.groupby("anio")["nacimientos"].sum()
else:
    S["total"] = por_anio(df_m["ini"].notna() | df_m["ini"].isna())
ANIOS = S.index.tolist()
Y0, Y1 = ANIOS[0], ANIOS[-1]



def cambio(s, a, b):
    return (s.loc[b] / s.loc[a] - 1) * 100


def ritmo(s, a, b):
    """Variación anual promedio (compuesta) entre los años a y b."""
    return ((s.loc[b] / s.loc[a]) ** (1 / (b - a)) - 1) * 100


def tarjeta(titulo="", cuerpo="", color="", bullets=None):
    inner = f"<h4>{titulo}</h4>" if titulo else ""
    inner += ("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>") if bullets else f"<p>{cuerpo}</p>"
    st.markdown(f'<div class="card {color}">{inner}</div>', unsafe_allow_html=True)


def bignum(valor, etiqueta, color):
    st.markdown(f'<div class="bignum"><div class="n" style="color:{color}">{valor}</div>'
                f'<div class="l">{etiqueta}</div></div>', unsafe_allow_html=True)


def nota(t):
    st.markdown(f'<div class="note">{t}</div>', unsafe_allow_html=True)


def estilo(fig, alto=430):
    fig.update_layout(height=alto, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=TEXT, family="Inter"), margin=dict(l=10, r=90, t=55, b=10),
                      legend=dict(orientation="h", y=-0.14), title_font=dict(size=16))
    fig.update_xaxes(gridcolor="#22345a", zeroline=False, dtick=1)
    fig.update_yaxes(gridcolor="#22345a", zeroline=False)
    return fig


def mostrar(fig, key=None):
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)


def capitulo(anchor, kicker, titulo):
    st.markdown(f'<div id="{anchor}"></div><div class="kicker">{kicker}</div>'
                f'<div class="title">{titulo}</div><div class="rule"></div>', unsafe_allow_html=True)


def grafico_hito(evento, principal, nombre_p, color_p, referencias, titulo, extra_vline=None, key=""):
    """
    Índice base 100 = año del hito. Muestra 3 años antes (si hay) como contexto y todo el período posterior.
    principal: Series. referencias: lista de (Series, nombre, color).
    Devuelve (cambio_principal, ritmo_antes, ritmo_despues).
    """
    x0 = max(Y0, evento - 3)
    anios = [a for a in ANIOS if x0 <= a <= Y1]
    f = go.Figure()
    f.add_vrect(x0=evento, x1=Y1 + 0.5, fillcolor="rgba(59,184,166,.07)", line_width=0)
    f.add_vline(x=evento, line_dash="dash", line_color=YELLOW, line_width=2)
    f.add_annotation(x=evento, y=1.07, yref="paper", text=f"<b>{evento}</b>", showarrow=False,
                     font=dict(color=YELLOW, size=13))
    if extra_vline:
        f.add_vline(x=extra_vline[0], line_dash="dot", line_color=MUTED, line_width=1)
        f.add_annotation(x=extra_vline[0], y=1.07, yref="paper", text=extra_vline[1], showarrow=False,
                         font=dict(color=MUTED, size=11))
    for serie_, nombre, color in referencias + [(principal, nombre_p, color_p)]:
        idx = (serie_ / serie_.loc[evento] * 100).loc[anios]
        es_p = serie_ is principal
        f.add_trace(go.Scatter(
            x=idx.index, y=idx.values, mode="lines+markers", name=nombre,
            line=dict(color=color, width=5 if es_p else 2.5, dash="solid" if es_p else "dot"),
            marker=dict(size=9 if es_p else 5),
            hovertemplate=nombre + " · %{x}: %{y:.1f}<extra></extra>"))
        f.add_annotation(x=Y1, y=idx.iloc[-1], text=f"<b>{idx.iloc[-1] - 100:+.0f}%</b>".replace("-", "−"),
                         showarrow=False, xanchor="left", xshift=8, font=dict(color=color, size=13 if es_p else 11))
    f.add_hline(y=100, line_color="#3a4f7a", line_width=1)
    f.update_layout(title=titulo)
    f.update_xaxes(range=[x0 - 0.3, Y1 + 0.9])
    f.update_yaxes(title_text=f"Índice (base 100 = {evento})")
    mostrar(estilo(f), key=key)
    return cambio(principal, evento, Y1), ritmo(principal, x0, evento), ritmo(principal, evento, Y1)


def indicadores(evento, nombre_p, c_p, c_ref, nombre_ref, r_antes, r_despues):
    a, b, c = st.columns(3)
    with a:
        bignum(fpct(c_p, 0), f"{nombre_p}<br>{evento} → {Y1}", CORAL)
    with b:
        bignum(fpct(c_ref, 0), f"{nombre_ref}<br>{evento} → {Y1}", BLUE)
    with c:
        bignum(f"{fpct(r_antes, 1)} → {fpct(r_despues, 1)}",
               "ritmo anual promedio<br>antes (hasta 3 años) → después", YELLOW)


def tabla_datos(cols, evento):
    with st.expander("Ver los datos de este gráfico"):
        t = S.loc[[a for a in ANIOS if a >= max(Y0, evento - 3)], cols].copy()
        t.columns = [f"{c} (nacimientos)" for c in cols]
        t.index.name = "Año"
        st.dataframe(t)


#herramientas para que funcione el historytelling
BASE = Path(__file__).resolve().parent
PROC = BASE / "DATA_PROCESADA"
BACKGROUNDS = BASE / "BACKGROUNDS"

GEOJSON_URL = "https://apis.datos.gob.ar/georef/api/v2.0/provincias.geojson"


def clave_prov(nombre) -> str:
    """Normaliza nombres de provincias para cruzar CSV con GeoJSON."""
    s = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode().lower().strip()
    if s.startswith("tierra del fuego"):
        return "tierra del fuego"
    if "ciudad" in s or "caba" in s or "capital federal" in s:
        return "caba"
    return s


df_prov = leer_csv("POBLACION", "nacimientos_provi_año.csv")
if df_prov is None or not {"provincia", "anio", "nacimientos"} <= set(df_prov.columns):
    st.error(
        "No encontré `DATA_PROCESADA/POBLACION/nacimientos_provi_año.csv` "
        "(con columnas provincia, anio, nacimientos). Ejecutá antes `poblacion.ipynb` "
        "y corré la app desde la carpeta raíz del proyecto."
    )
    st.stop()

df_prov = df_prov.copy()
df_prov["anio"] = pd.to_numeric(df_prov["anio"]).astype(int)
df_prov["nacimientos"] = pd.to_numeric(df_prov["nacimientos"])

suma_prov = df_prov.groupby("anio", as_index=False)["nacimientos"].sum()
df_tot = leer_csv("POBLACION", "nacimientos_total_año.csv")
if df_tot is not None and {"anio", "nacimientos"} <= set(df_tot.columns):
    serie = df_tot.groupby("anio", as_index=False)["nacimientos"].sum()
    _cmp = suma_prov.merge(serie, on="anio", suffixes=("_prov", "_tot"))
    _d = ((_cmp["nacimientos_prov"] / _cmp["nacimientos_tot"] - 1) * 100).abs()
    NOTA_FUENTES = (f"La serie nacional usa el archivo de totales por año. El detalle por provincia y por edad de la madre "
                    f"proviene de otro archivo y suma entre {_d.min():.1f}% y {_d.max():.1f}% menos, por eso las cifras no coinciden exactamente.").replace(".", ",")
else:
    serie = suma_prov
    NOTA_FUENTES = "Serie nacional calculada como suma de las 24 jurisdicciones."
serie = serie.sort_values("anio").reset_index(drop=True)
serie["var_pct"] = serie["nacimientos"].pct_change() * 100
ANIOS = serie["anio"].tolist()
Y0, Y1 = ANIOS[0], ANIOS[-1]
N0 = int(serie.loc[serie.anio == Y0, "nacimientos"].iloc[0])
N1 = int(serie.loc[serie.anio == Y1, "nacimientos"].iloc[0])
fila_pico = serie.loc[serie["nacimientos"].idxmax()]
YP, NP = int(fila_pico["anio"]), int(fila_pico["nacimientos"])
CAIDA_PICO = (N1 / NP - 1) * 100            # del máximo al último año
fila_peor = serie.loc[serie["var_pct"].idxmin()] if serie["var_pct"].notna().any() else None



def fpct(n, dec=1, signo=False) -> str:
    s = f"{n:+.{dec}f}" if signo else f"{n:.{dec}f}"
    return s.replace(".", ",").replace("-", "−") + "%"


def sube_baja(a, b) -> str:
    return "bajaron" if b < a else "subieron"


def capitulo(anchor, kicker, titulo, bajada=""):
    html = (f'<div id="{anchor}"></div><div class="kicker">{kicker}</div>'
            f'<div class="title">{titulo}</div><div class="rule"></div>')
    if bajada:
        html += f'<div class="lead">{bajada}</div>'
    st.markdown(html, unsafe_allow_html=True)


def bignum(valor, etiqueta, color):
    st.markdown(f'<div class="bignum"><div class="n" style="color:{color}">{valor}</div>'
                f'<div class="l">{etiqueta}</div></div>', unsafe_allow_html=True)


def tarjeta(titulo="", cuerpo="", color="", bullets=None):
    inner = f"<h4>{titulo}</h4>" if titulo else ""
    if bullets:
        inner += "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
    else:
        inner += f"<p>{cuerpo}</p>"
    st.markdown(f'<div class="card {color}">{inner}</div>', unsafe_allow_html=True)


def callout(texto, warn=False):
    st.markdown(f'<div class="callout {"warn" if warn else ""}">{texto}</div>', unsafe_allow_html=True)


def nota(texto):
    st.markdown(f'<div class="note">{texto}</div>', unsafe_allow_html=True)


def fuente(texto):
    st.markdown(f'<div class="src">Fuente: {texto}</div>', unsafe_allow_html=True)


def estilo(fig: go.Figure, alto=380, leyenda=False) -> go.Figure:
    fig.update_layout(
        height=alto, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Inter"), margin=dict(l=10, r=10, t=50, b=10),
        showlegend=leyenda, title_font=dict(size=16),
        legend=dict(orientation="h", y=-0.15),
    )
    fig.update_xaxes(gridcolor="#22345a", zeroline=False)
    fig.update_yaxes(gridcolor="#22345a", zeroline=False)
    return fig


def mostrar(fig, key=None):
    """Compatible con versiones nuevas y viejas de Streamlit."""
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)


def dona(valor, color, titulo, alto=210):
    f = go.Figure(go.Pie(values=[valor, max(100 - valor, 0)], hole=0.72, sort=False,
                         marker=dict(colors=[color, "#22345a"]), textinfo="none", hoverinfo="skip"))
    f.add_annotation(text=f"<b>{fpct(valor, 0)}</b>", x=0.5, y=0.5, showarrow=False,
                     font=dict(size=26, color=color))
    f.update_layout(title=dict(text=titulo, x=0.5, font=dict(size=14)))
    return estilo(f, alto)







#pestañás
  
    #storytelling
if st.session_state.ver_storytelling:

    with st.sidebar:
    
        lista_anios = list(df_agrupado.anio.unique())[::-1]
        anio_seleccionado = st.selectbox("Seleccione un año", lista_anios)
    
        st.markdown("""
            <div class='indice-card'>

            <h2>📚 Índice</h2>

            <ul>
            <li><a href="#c1">01 · El dato que cambia la historia</a></li>
            <li><a href="#c2">02 · El descenso no ocurrió de golpe</a></li>
            <li><a href="#c3">03 · Año a año</a></li>
            <li><a href="#c4">04 · Argentina no es una sola realidad</a></li>
            <li><a href="#c5">05 · La edad de las madres</a></li>
            <li><a href="#c6">06 · El contexto económico y de salud</a></li>
            <li><a href="#c7">07 · ¿Por qué baja? ¿Por qué importa?</a></li>
            <li><a href="#c8">08 · Conclusiones y fuentes</a></li>
            </ul>

            </div>
            """, unsafe_allow_html=True)


    st.markdown("""
    
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
        }}

        [data-testid="block-container"] {{
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1300px;
        }}

        [data-testid="stAppViewContainer"] {{
            {background_style}
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #EAF0FA !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}

        section[data-testid="stSidebar"] {{
            background: #0B1428 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        /* Contenedores Glassmorphic principales */
        div[data-testid="stVerticalBlock"] > div[dir="ltr"] > div {{
            background: rgba(26, 43, 74, 0.65) !important;
            backdrop-filter: blur(14px) saturate(180%);
            -webkit-backdrop-filter: blur(14px) saturate(180%);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            padding: 20px;
            margin-bottom: 15px;
        }}

        /* Botones unificados */
        .stButton>button {{
            background: rgba(255, 255, 255, 0.12) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(6px);
            transition: all 0.25s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .stButton>button:hover {{
            background: rgba(59, 184, 166, 0.3) !important;
            border-color: #3BB8A6 !important;
            color: #ffffff !important;
            transform: translateY(-1px);
        }}

        /* Tarjetas HTML personalizadas */
        .card {{
            background: rgba(26, 43, 74, 0.8);
            border-radius: 16px;
            padding: 20px;
            margin: 12px 0;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-left: 5px solid #3BB8A6;
            backdrop-filter: blur(10px);
        }}
        .card.blue {{ border-left-color: #3F7FC4; }}
        .card.yellow {{ border-left-color: #F5B942; }}
        .card.coral {{ border-left-color: #E8605F; }}

        .card h4 {{ margin: 0 0 8px 0; color: #ffffff; font-size: 1.1rem; font-weight: 700; }}
        .card p, .card li {{ color: #EAF0FA; font-size: 0.95rem; line-height: 1.5; margin: 0; }}

        /* Big Numbers / Métricas */
        .bignum {{
            text-align: center;
            padding: 18px 10px;
            background: rgba(26, 43, 74, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}
        .bignum .n {{ font-size: 2.5rem; font-weight: 900; line-height: 1.05; }}
        .bignum .l {{ color: #9FB0CC; margin-top: 6px; font-size: 0.88rem; line-height: 1.3; }}

        /* Callouts y Encabezados */
        .hero {{
            padding: 2.5rem 2rem;
            border-radius: 20px;
            margin-bottom: 25px;
            text-align: center;
            background: radial-gradient(circle at 85% 20%, rgba(29, 58, 107, 0.8) 0%, rgba(15, 27, 51, 0.9) 62%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}
        .hero h1 {{ font-size: 2.8rem; font-weight: 900; color: #F5B942; margin-bottom: 10px; text-transform: uppercase; }}
        .hero .sub {{ font-size: 1.2rem; color: #EAF0FA; font-style: italic; }}

        .kicker {{ color: #3BB8A6; font-weight: 800; letter-spacing: .1em; font-size: 0.85rem; margin-top: 2rem; text-transform: uppercase; }}
        .title {{ font-size: 1.8rem; font-weight: 800; color: #ffffff; margin: 0.3rem 0; }}
        .rule {{ width: 60px; height: 4px; background: #3BB8A6; border-radius: 4px; margin: 0.5rem 0 1.2rem 0; }}

        .callout {{
            background: linear-gradient(135deg, rgba(59,184,166,0.25), rgba(63,127,196,0.25));
            border-radius: 14px;
            padding: 18px;
            font-size: 1.1rem;
            font-weight: 700;
            color: #F5B942;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
            margin: 15px 0;
        }}

        .note {{ color: #9FB0CC; font-size: 0.88rem; font-style: italic; margin: 8px 0; }}
        .src {{ color: #7e90b0; font-size: 0.8rem; margin-top: 5px; }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: #ffffff !important;
        }}
        </style>
        """, unsafe_allow_html=True)

    

    def capitulo(anchor, kicker, titulo, bajada=""):
        html = (f'<div id="{anchor}"></div><div class="kicker">{kicker}</div>'
                f'<div class="title">{titulo}</div><div class="rule"></div>')
        if bajada:
            html += f'<div class="lead">{bajada}</div>'
        st.markdown(html, unsafe_allow_html=True)

    def bignum(valor, etiqueta, color):
        st.markdown(f'<div class="bignum"><div class="n" style="color:{color}">{valor}</div>'
                    f'<div class="l">{etiqueta}</div></div>', unsafe_allow_html=True)

    def tarjeta(titulo="", cuerpo="", color="", bullets=None):
        inner = f"<h4>{titulo}</h4>" if titulo else ""
        if bullets:
            inner += "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
        else:
            inner += f"<p>{cuerpo}</p>"
        st.markdown(f'<div class="card {color}">{inner}</div>', unsafe_allow_html=True)

    def callout(texto, warn=False):
        st.markdown(f'<div class="callout {"warn" if warn else ""}">{texto}</div>', unsafe_allow_html=True)

    def nota(texto):
        st.markdown(f'<div class="note">{texto}</div>', unsafe_allow_html=True)

    def fuente(texto):
        st.markdown(f'<div class="src">Fuente: {texto}</div>', unsafe_allow_html=True)

    def estilo(fig: go.Figure, alto=380, leyenda=False) -> go.Figure:
        fig.update_layout(
            height=alto, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, family="Inter"), margin=dict(l=10, r=10, t=50, b=10),
            showlegend=leyenda, title_font=dict(size=16),
            legend=dict(orientation="h", y=-0.15),
        )
        fig.update_xaxes(gridcolor="#22345a", zeroline=False)
        fig.update_yaxes(gridcolor="#22345a", zeroline=False)
        return fig

    def mostrar(fig, key=None):
        try:
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=key)
        except TypeError:
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=key)

    def dona_st(valor, color, titulo, alto=210):
        f = go.Figure(go.Pie(values=[valor, max(100 - valor, 0)], hole=0.72, sort=False,
                             marker=dict(colors=[color, "#22345a"]), textinfo="none", hoverinfo="skip"))
        f.add_annotation(text=f"<b>{fpct(valor, 0)}</b>", x=0.5, y=0.5, showarrow=False,
                         font=dict(size=26, color=color))
        f.update_layout(title=dict(text=titulo, x=0.5, font=dict(size=14)))
        return estilo(f, alto)

    # portada
    st.markdown('<div id="inicio"></div>', unsafe_allow_html=True)
    chips = "".join(f'<span class="chip">{a}</span>' for a in sorted({Y0, YP, Y1}))
    st.markdown(
        f"""
        <div class="hero">
        <h1>ARGENTINA:<br>NATALIDAD EN TRANSFORMACIÓN</h1>
        <div class="sub">Una historia contada a través de los nacimientos registrados</div>
        <div class="meta">Storytelling demográfico · Análisis de la natalidad {Y0}–{Y1}</div>
        {chips}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Fuentes principales: Estadísticas Vitales (DEIS · Ministerio de Salud), datos abiertos de datos.gob.ar.")


    #capitulo 1
    capitulo("c1", "01 · EL DATO QUE CAMBIA LA HISTORIA", "La pregunta no es solo cuántos nacen, sino cómo está cambiando el país")
    a, b, c = st.columns([5, 1, 5])
    with a:
        bignum(fmt(NP), f"nacimientos registrados en {YP} (el mas alto)", TEAL)
    with b:
        st.markdown(f"<div style='text-align:center;font-size:2.4rem;color:{YELLOW};padding-top:1.3rem'>→</div>", unsafe_allow_html=True)
    with c:
        bignum(fmt(N1), f"nacimientos registrados en {Y1} (el mas bajo)", CORAL)
    callout(f"Una variación de {fpct(CAIDA_PICO, signo=True)} entre {YP} y {Y1}")
    nota(f"Son {fmt(abs(NP - N1))} nacimientos {'menos' if N1 < NP else 'más'} que en {YP}.")
    fuente("Estadísticas Vitales, DEIS (datos.gob.ar).")

    #capitulo 2
    capitulo("c2", "02 · EL DESCENSO NO OCURRIÓ DE GOLPE", "Mirá cómo evolucionó año por año", f"Serie anual completa {Y0}–{Y1}.")
    g1, g2 = st.columns([3, 2])
    with g1:
        f = go.Figure()
        f.add_trace(go.Scatter(x=serie["anio"], y=serie["nacimientos"], mode="lines+markers",
                               line=dict(color=TEAL, width=4), marker=dict(size=8, color=TEAL),
                               fill="tozeroy", fillcolor="rgba(59,184,166,.12)",
                               hovertemplate="%{x}: %{y:,.0f} nacimientos<extra></extra>"))
        sel = serie[serie.anio == anio_seleccionado]
        f.add_trace(go.Scatter(x=sel["anio"], y=sel["nacimientos"], mode="markers",
                               marker=dict(size=16, color=CORAL, line=dict(color="#fff", width=2)), hoverinfo="skip"))
        f.update_layout(title="Nacimientos registrados por año")
        f.update_xaxes(dtick=1)
        f.update_yaxes(rangemode="tozero")
        mostrar(estilo(f, 400))
    with g2:
        v = serie.dropna(subset=["var_pct"])
        f = go.Figure(go.Bar(
            x=v["anio"], y=v["var_pct"],
            marker_color=[CORAL if x < 0 else TEAL for x in v["var_pct"]],
            text=[fpct(x, 1) for x in v["var_pct"]], textposition="outside",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
        f.update_layout(title="Variación respecto al año anterior")
        f.update_xaxes(dtick=1, tickangle=-45)
        mostrar(estilo(f, 400))

    if fila_peor is not None:
        callout(f"La mayor variación anual fue en {int(fila_peor['anio'])}: {fpct(fila_peor['var_pct'], signo=True)}", warn=True)

    #capitulo 3
    capitulo("c3", f"03 · EL AÑO {anio_seleccionado} EN DETALLE", "¿Qué pasó entre un año y el anterior?", "Selecciona en el Sidebar el año para realizar la comparacion")
    pivote = df_prov.pivot_table(index="provincia", columns="anio", values="nacimientos", aggfunc="sum")
    n_sel = int(serie.loc[serie.anio == anio_seleccionado, "nacimientos"].iloc[0])

    if anio_seleccionado > Y0:
        n_prev = int(serie.loc[serie.anio == anio_seleccionado - 1, "nacimientos"].iloc[0])
        dif = n_sel - n_prev
        var = (n_sel / n_prev - 1) * 100
        a, b, c = st.columns(3)
        with a:
            bignum(fmt(n_prev), f"nacimientos en {anio_seleccionado - 1}", TEAL)
        with b:
            bignum(f"{'+' if dif > 0 else '−'}{fmt(abs(dif))}", "diferencia absoluta", YELLOW)
        with c:
            bignum(fmt(n_sel), f"nacimientos en {anio_seleccionado}", CORAL)
        callout(f"Variación interanual: {fpct(var, signo=True)}")

        cambios = (pivote[anio_seleccionado] - pivote[anio_seleccionado - 1]).dropna().sort_values(ascending=False)
        p_alza = round((cambios > 0).mean() * 100)
        p_baja = round((cambios < 0).mean() * 100)
        m1, m2, m3, m4 = st.columns([1.3, 1.3, 1, 1])
        m1.metric(f"▲ {cambios.index[0]}", fmt(pivote.loc[cambios.index[0], anio_seleccionado]), delta=f"{cambios.iloc[0]:+,.0f}".replace(",", "."))
        m2.metric(f"▼ {cambios.index[-1]}", fmt(pivote.loc[cambios.index[-1], anio_seleccionado]), delta=f"{cambios.iloc[-1]:+,.0f}".replace(",", "."))
        with m3:
            mostrar(dona_st(p_alza, TEAL, "Provincias en alza"), key="d_alza")
        with m4:
            mostrar(dona_st(p_baja, CORAL, "Provincias a la baja"), key="d_baja")
        nota("Extremos: provincia con mayor suba y mayor baja de nacimientos respecto al año anterior.")
    else:
        bignum(fmt(n_sel), f"nacimientos en {anio_seleccionado} (primer año de la serie)", TEAL)

    #capitulo 4
    capitulo("c4", "04 · ARGENTINA NO ES UNA SOLA REALIDAD", "El descenso nacional convive con diferencias territoriales")
    orden_prov = pivote.sum(axis=1).sort_values(ascending=False).index.tolist()
    t1, t2, t3 = st.tabs(["📊 Ranking", "🔥 Mapa de calor histórico", "🗺️ Mapa"])

    with t1:
        d = pivote[anio_seleccionado].dropna().sort_values()
        r1, r2 = st.columns([3, 2])
        with r1:
            f = go.Figure(go.Bar(x=d.values, y=d.index, orientation="h", marker=dict(color=d.values, colorscale=paleta), hovertemplate="%{y}: %{x:,.0f} nacimientos<extra></extra>"))
            f.update_layout(title=f"Nacimientos por provincia · {anio_seleccionado}")
            mostrar(estilo(f, 640))
        with r2:
            tabla = d.sort_values(ascending=False).reset_index()
            tabla.columns = ["Provincia", "Nacimientos"]
            cfg = {"Nacimientos": st.column_config.ProgressColumn("Nacimientos", format="%d", min_value=0, max_value=int(tabla["Nacimientos"].max()))}
            st.dataframe(tabla, hide_index=True, column_config=cfg, height=600, use_container_width=True)

    with t2:
        modo_h = st.radio("Mostrar", ["Nacimientos", "Variación % vs primer año"], horizontal=True, key="modo_h")
        if modo_h == "Nacimientos":
            z = pivote.loc[orden_prov]
            titulo_h, fmt_h = "Nacimientos por provincia y año", "%{z:,.0f}"
        else:
            z = (pivote.loc[orden_prov].div(pivote.loc[orden_prov, Y0], axis=0) - 1) * 100
            titulo_h, fmt_h = f"Variación % respecto de {Y0}", "%{z:.1f}%"
        f = go.Figure(go.Heatmap(z=z.values, x=[str(c) for c in z.columns], y=z.index, colorscale=paleta, xgap=1, ygap=1, hovertemplate="%{y} · %{x}: " + fmt_h + "<extra></extra>"))
        f.update_layout(title=titulo_h)
        f.update_yaxes(autorange="reversed")
        mostrar(estilo(f, 680))

    with t3:
        geo = cargar_geojson()
        if geo is not None:
            modo_m = st.radio("Mostrar", ["Nacimientos del año", f"Índice (base 100 = {Y0})"], horizontal=True, key="modo_m")
            nombres_geo = {clave_prov(ft["properties"]["nombre"]): ft["properties"]["nombre"] for ft in geo["features"]}
            dm = pd.DataFrame({"base": pivote[Y0], "actual": pivote[anio_seleccionado]}).dropna().reset_index()
            dm["geo"] = dm["provincia"].map(lambda p: nombres_geo.get(clave_prov(p)))
            dm = dm.dropna(subset=["geo"])
            dm["valor"], tit_cb = (dm["actual"], "Nacimientos") if modo_m == "Nacimientos del año" else (dm["actual"] / dm["base"] * 100, f"Índice ({Y0}=100)")
            f = go.Figure(go.Choropleth(geojson=geo, locations=dm["geo"], z=dm["valor"], featureidkey="properties.nombre", colorscale=paleta, marker_line_color="#0F1B33", marker_line_width=0.6))
            f.update_geos(lataxis_range=[-56, -21.5], lonaxis_range=[-74.5, -53], visible=False, bgcolor="rgba(0,0,0,0)")
            f.update_layout(title=f"{tit_cb} · {anio_seleccionado}")
            mostrar(estilo(f, 680))

    
    #capitulo 5
    capitulo("c5", "05 · TAMBIÉN CAMBIA LA EDAD AL MOMENTO DE TENER HIJOS",
            "¿Cuánto pesa la maternidad adolescente?")
    df_m = leer_csv("POBLACION", "madres_grupo_edad_total.csv")
    share = None
    if df_m is None or not {"anio", "grupo_etario_madre", "cantidad"} <= set(df_m.columns):
        st.info("Falta `DATA_PROCESADA/POBLACION/madres_grupo_edad_total.csv` (se genera en poblacion.ipynb).")
    else:
        df_m = df_m.copy()
        df_m["anio"] = df_m["anio"].astype(int)

        def inicio_edad(txt):
            m = re.search(r"\d+", str(txt))
            return int(m.group()) if m else None

        df_m["ini"] = df_m["grupo_etario_madre"].map(inicio_edad)
        tot = df_m.groupby("anio")["cantidad"].sum()
        menor20 = df_m[df_m["ini"].fillna(99) < 20].groupby("anio")["cantidad"].sum().reindex(tot.index).fillna(0)
        share = (menor20 / tot * 100).rename("pct")

        y_a, y_b = int(share.index.min()), int(share.index.max())
        cA, cB, cC = st.columns([1, 1, 2])
        with cA:
            mostrar(dona(share[y_a], TEAL, str(y_a), 260), key="m_a")
        with cB:
            mostrar(dona(share[y_b], CORAL, str(y_b), 260), key="m_b")
        with cC:
            f = go.Figure(go.Scatter(x=share.index, y=share.values, mode="lines+markers",
                                    line=dict(color=YELLOW, width=4), marker=dict(size=8),
                                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
            f.update_layout(title="% de nacimientos de madres menores de 20 años")
            f.update_xaxes(dtick=1)
            f.update_yaxes(rangemode="tozero", ticksuffix="%")
            mostrar(estilo(f, 260))
        callout(f"La proporción pasó de {fpct(share[y_a])} en {y_a} a {fpct(share[y_b])} en {y_b}")

        with st.expander("Ver nacimientos por grupo de edad de la madre"):
            pv = df_m.pivot_table(index="anio", columns="grupo_etario_madre", values="cantidad", aggfunc="sum")
            cols = sorted(pv.columns, key=lambda c: (inicio_edad(c) is None, inicio_edad(c) or 0))
            f = go.Figure()
            for col in cols:
                f.add_trace(go.Scatter(x=pv.index, y=pv[col], mode="lines+markers", name=str(col)))
            f.update_layout(title="Nacimientos según grupo de edad de la madre")
            f.update_xaxes(dtick=1)
            mostrar(estilo(f, 420, leyenda=True))
        nota("Es una asociación descriptiva: no debe atribuirse a una única causa sin análisis adicional.")

   

   #capitulo 6
    capitulo("c6", "06 · EL CONTEXTO ECONÓMICO Y DE SALUD",
            "¿Qué pasaba en la economía mientras bajaban los nacimientos?",
            "La línea punteada es la serie de nacimientos (eje derecho). "
            "Se muestran juntas para dar contexto, no para afirmar causas.")


    def grafico_contexto(x, y, titulo, nombre_y, tipo="line"):
        f = make_subplots(specs=[[{"secondary_y": True}]])
        if tipo == "bar":
            f.add_trace(go.Bar(x=x, y=y, name=nombre_y, marker_color=BLUE), secondary_y=False)
        else:
            f.add_trace(go.Scatter(x=x, y=y, name=nombre_y, mode="lines+markers",
                                line=dict(color=BLUE, width=3)), secondary_y=False)
        f.add_trace(go.Scatter(x=serie["anio"], y=serie["nacimientos"], name="Nacimientos",
                            mode="lines", line=dict(color=CORAL, width=3, dash="dot")), secondary_y=True)
        f.update_layout(title=titulo)
        f.update_xaxes(dtick=1)
        f.update_yaxes(title_text=nombre_y, secondary_y=False)
        f.update_yaxes(title_text="Nacimientos", secondary_y=True, showgrid=False)
        return estilo(f, 400, leyenda=True)


    e1, e2, e3 = st.tabs(["💸 Inflación", "💵 Salario mínimo", "🏥 Inversión en salud"])

    with e1:
        d = leer_csv("ECONOMIA", "inflacion_2012_2024.csv")
        if d is not None and {"fecha", "valor"} <= set(d.columns):
            d["fecha"] = d["fecha"].astype(int)
            i1, i2 = st.columns([3, 2])
            with i1:
                mostrar(grafico_contexto(d["fecha"], d["valor"], "Inflación acumulada anual (%)", "Inflación (%)", "bar"), key="ctx1")
            with i2:
                vi = leer_csv("ECONOMIA", "variacion_inflacion_2012_2024.csv")
                if vi is not None and {"fecha", "variacion"} <= set(vi.columns):
                    vi = vi.dropna(subset=["variacion"])
                    f = go.Figure(go.Bar(x=vi["fecha"].astype(int), y=vi["variacion"],
                                        marker_color=[CORAL if v > 0 else TEAL for v in vi["variacion"]],
                                        hovertemplate="%{x}: %{y:.1f}%<extra></extra>"))
                    f.update_layout(title="Cambio de la inflación anual vs el año anterior (%)")
                    f.update_xaxes(dtick=1, tickangle=-45)
                    mostrar(estilo(f, 400), key="ctx1b")
            nota("A la derecha: cuánto cambió la inflación anual respecto de la del año previo "
                "(+50% significa que fue 1,5 veces la del año anterior).")
            fuente("Serie de inflación interanual, procesada en economia.ipynb.")
        else:
            st.info("Falta `DATA_PROCESADA/ECONOMIA/inflacion_2012_2024.csv`.")

    with e2:
        d = leer_csv("ECONOMIA", "salario_min_desde_2012.csv")
        col_sal = "salario_minimo_vital_movil_mensual"
        if d is not None and {"indice_tiempo", col_sal} <= set(d.columns):
            d["indice_tiempo"] = pd.to_datetime(d["indice_tiempo"])
            d = d[d["indice_tiempo"].dt.month == 12].copy()
            d["anio"] = d["indice_tiempo"].dt.year
            mostrar(grafico_contexto(d["anio"], d[col_sal], "Salario mínimo vital y móvil (diciembre de cada año)",
                                    "Pesos corrientes"), key="ctx2")
            nota("Valores en pesos corrientes (sin ajustar por inflación): el aumento nominal no implica mayor poder de compra.")
            vs = leer_csv("ECONOMIA", "variacion_salario_min_desde_2012.csv")
            infl = leer_csv("ECONOMIA", "inflacion_2012_2024.csv")
            if (vs is not None and infl is not None and {"anio", "variacion"} <= set(vs.columns)
                    and {"fecha", "valor"} <= set(infl.columns)):
                vs = vs.dropna(subset=["variacion"]).copy()
                vs["anio"] = vs["anio"].astype(int)
                im = infl.assign(fecha=infl["fecha"].astype(int)).set_index("fecha")["valor"]
                vs["infl_prev"] = (vs["anio"] - 1).map(im)
                f = go.Figure()
                f.add_trace(go.Bar(x=vs["anio"], y=vs["variacion"], name="Salario mínimo (ene a ene)", marker_color=BLUE))
                f.add_trace(go.Bar(x=vs["anio"], y=vs["infl_prev"], name="Inflación del año anterior", marker_color=YELLOW))
                f.update_layout(barmode="group", title="Variación del salario mínimo vs inflación (%)")
                f.update_xaxes(dtick=1)
                mostrar(estilo(f, 380, leyenda=True), key="ctx2b")
                nota("Comparación aproximada: la variación de enero a enero de cada año se contrasta con la inflación "
                    "acumulada del año anterior.")
            fuente("Consejo del Salario / datos.gob.ar, procesado en economia.ipynb.")
        else:
            st.info("Falta `DATA_PROCESADA/ECONOMIA/salario_min_desde_2012.csv`.")

    with e3:
        s1 = leer_csv("SALUD", "inversion_salud_año.csv")
        s2 = leer_csv("SALUD", "inversion_investigacion_salud_año.csv")
        ok1 = s1 is not None and {"anio", "inv_id_pesos_corr"} <= set(s1.columns)
        ok2 = s2 is not None and {"anio", "inv_id_pesos_corr"} <= set(s2.columns)
        if ok1 or ok2:
            k1, k2 = st.columns(2)
            if ok1:
                with k1:
                    mostrar(grafico_contexto(s1["anio"], s1["inv_id_pesos_corr"], "Inversión en salud",
                                            "Millones de pesos"), key="ctx3")
            if ok2:
                with k2:
                    mostrar(grafico_contexto(s2["anio"], s2["inv_id_pesos_corr"], "Inversión en investigación médica",
                                            "Millones de pesos"), key="ctx4")
            nota("Millones de pesos corrientes, sin ajuste por inflación.")
            fuente("datos.gob.ar, procesado en salud.ipynb.")
        else:
            st.info("Faltan los CSV de `DATA_PROCESADA/SALUD/`.")

    

    #capitulo 7

    capitulo("c7", "07 · ¿POR QUÉ ESTÁ BAJANDO? ¿POR QUÉ IMPORTA?",
            "Los datos muestran el cambio; explicar sus causas requiere más evidencia",
            "Cada bloque se respalda abajo con los datos del proyecto.")
    a, b, c = st.columns(3)
    with a:
        tarjeta("Hipótesis a investigar",
                "Edad al tener hijos, decisiones reproductivas, condiciones económicas, acceso a anticoncepción, "
                "educación y cambios culturales.", "blue")
    with b:
        tarjeta("Qué haría falta",
                "Cruzar fecundidad, edades, estructura poblacional, condiciones socioeconómicas y series comparables.")
    with c:
        tarjeta("👥 Estructura por edades",
                "Si la fecundidad baja por períodos prolongados, cambia la relación entre grupos etarios; "
                "también influyen mortalidad y migración.", "yellow")
    st.write("")
    st.markdown("#### 🔎 La evidencia disponible en este proyecto")
    h1, h2, h3 = st.tabs(["🧭 Hipótesis: qué dicen los datos", "🧩 Un primer cruce de datos", "👥 Estructura por edades"])

    #hipotesis
    with h1:
        if share is None:
            st.info("Falta `madres_grupo_edad_total.csv` para evaluar la hipótesis de la edad materna.")
        else:
            pv = df_m.pivot_table(index="anio", columns="grupo_etario_madre", values="cantidad", aggfunc="sum")
            comp = pv.div(pv.sum(axis=1), axis=0) * 100
            cols_ord = sorted(pv.columns, key=lambda c: (inicio_edad(c) is None, inicio_edad(c) or 0))
            mayores30 = df_m[df_m["ini"].fillna(0) >= 30].groupby("anio")["cantidad"].sum().reindex(tot.index).fillna(0) / tot * 100
            f = go.Figure()
            for col in cols_ord:
                f.add_trace(go.Bar(x=comp.index, y=comp[col], name=str(col),
                                hovertemplate="%{x} · " + str(col) + ": %{y:.1f}%<extra></extra>"))
            f.update_layout(barmode="stack", title="¿A qué edad tienen hijos? Composición de los nacimientos (%)")
            f.update_xaxes(dtick=1)
            f.update_yaxes(ticksuffix="%", range=[0, 100])
            mostrar(estilo(f, 400, leyenda=True), key="hip_edad")
            st.markdown(
                f"""
    | Hipótesis  **Edad al tener hijos** - Madres menores de 20: {fpct(share[y_a])} en {y_a} → {fpct(share[y_b])} en {y_b}. Madres de 30 o más: {fpct(mayores30[y_a])} → {fpct(mayores30[y_b])}. |

    """
            )
            nota("La edad materna cambió, pero eso describe quiénes tienen hijos, no explica por qué hay menos nacimientos.")

    #cruce de datos
    with h2:
        pf = leer_csv("POBLACION", "poblacion_no_extranjera_edad_f.csv")
        pm = leer_csv("POBLACION", "poblacion_no_extranjera_edad_m.csv")
        ok_pop = all(x is not None and {"nombre_provincia", "cantidad"} <= set(x.columns) for x in (pf, pm))
        if not ok_pop:
            st.info("Faltan `poblacion_no_extranjera_edad_f.csv` y/o `_m.csv` en DATA_PROCESADA/POBLACION.")
        else:
            pop = pd.DataFrame({"mujeres": pf.set_index("nombre_provincia")["cantidad"],
                                "varones": pm.set_index("nombre_provincia")["cantidad"]}).reset_index()
            pop["k"] = pop["nombre_provincia"].map(clave_prov)
            cr = pd.DataFrame({"provincia": pivote.index, "nac": pivote[Y1].values})
            cr["k"] = cr["provincia"].map(clave_prov)
            cr = cr.merge(pop[["k", "mujeres", "varones"]], on="k", how="inner")
            cr["por_hab"] = cr["nac"] / (cr["mujeres"] + cr["varones"]) * 1000
            cr["por_muj"] = cr["nac"] / cr["mujeres"] * 1000

            ind = st.radio("Indicador", ["Nacimientos cada 1.000 habitantes (tasa bruta aproximada)",
                                        "Nacimientos cada 1.000 mujeres"], horizontal=True, key="ind_cruce")
            col_i = "por_hab" if ind.startswith("Nacimientos cada 1.000 habitantes") else "por_muj"
            dd = cr.sort_values(col_i)
            f = go.Figure(go.Bar(x=dd[col_i], y=dd["provincia"], orientation="h",
                                marker=dict(color=dd[col_i], colorscale=paleta),
                                text=[f"{v:.1f}".replace(".", ",") for v in dd[col_i]], textposition="outside",
                                hovertemplate="%{y}: %{x:.1f}<extra></extra>"))
            f.update_layout(title=f"{ind} · nacimientos {Y1}")
            f.update_xaxes(range=[0, dd[col_i].max() * 1.15])
            mostrar(estilo(f, 640), key="cruce")
            top, low = cr.sort_values(col_i).iloc[-1], cr.sort_values(col_i).iloc[0]
            callout(f"{top['provincia']} tiene {top[col_i]:.1f} y {low['provincia']} {low[col_i]:.1f}".replace(".", ","))
            nota(f"Cruce de nacimientos {Y1} (por edad de la madre) con la población de agosto de 2024 (solo personas con "
                "nacionalidad y nacimiento argentinos). Es un indicador aproximado: sirve para comparar provincias entre sí, "
                "no reemplaza a la tasa oficial.")
            tarjeta("Qué seguiría faltando", color="yellow", bullets=[
                "Fecundidad por edad: nacimientos sobre mujeres de 15 a 49 años (hoy se usa toda la población femenina).",
                "Población por provincia y por año, no solo la de agosto de 2024.",
                "Variables socioeconómicas por provincia (ingresos, educación, cobertura de salud).",
            ])

    #estructura por edades
    with h3:
        piram = leer_csv("POBLACION", "piramide_poblacion.csv")
        if piram is None or not {"edad_quinquenal", "masculinos", "femeninos"} <= set(piram.columns):
            st.info("Falta `DATA_PROCESADA/POBLACION/piramide_poblacion.csv`.")
        else:
            piram = piram.copy()
            piram["tot"] = piram["masculinos"].abs() + piram["femeninos"].abs()
            piram["ini"] = piram["edad_quinquenal"].map(lambda t: int(re.search(r"\d+", str(t)).group()))
            T = piram["tot"].sum()
            p014 = piram[piram["ini"] < 15]["tot"].sum() / T * 100
            p65 = piram[piram["ini"] >= 65]["tot"].sum() / T * 100
            mayores_x100 = piram[piram["ini"] >= 65]["tot"].sum() / piram[piram["ini"] < 15]["tot"].sum() * 100
            q1, q2, q3 = st.columns(3)
            q1.metric("Población de 0 a 14 años", fpct(p014))
            q2.metric("Población de 65 años o más", fpct(p65))
            q3.metric("Mayores de 65 por cada 100 menores de 15", f"{mayores_x100:.0f}")

            mx = max(piram["masculinos"].abs().max(), piram["femeninos"].abs().max())
            paso = 10 ** (len(str(int(mx))) - 1)
            ticks = [i * paso for i in range(-int(mx // paso) - 1, int(mx // paso) + 2)]
            f = go.Figure()
            f.add_trace(go.Bar(y=piram["edad_quinquenal"], x=-piram["masculinos"].abs(), orientation="h",
                            name="Varones", marker_color=BLUE, customdata=piram["masculinos"].abs(),
                            hovertemplate="%{y}: %{customdata:,.0f}<extra>Varones</extra>"))
            f.add_trace(go.Bar(y=piram["edad_quinquenal"], x=piram["femeninos"].abs(), orientation="h",
                            name="Mujeres", marker_color=CORAL,
                            hovertemplate="%{y}: %{x:,.0f}<extra>Mujeres</extra>"))
            f.update_layout(barmode="relative", title="Pirámide poblacional · agosto 2024")
            f.update_xaxes(tickvals=ticks, ticktext=[fmt(abs(t)) for t in ticks])
            mostrar(estilo(f, 600, leyenda=True), key="piramide")

            g04 = piram.loc[piram["ini"] == 0, "tot"].sum()
            g1014 = piram.loc[piram["ini"] == 10, "tot"].sum()
            callout(f"La base de la pirámide se angosta: hay {fpct(abs((g04 / g1014 - 1) * 100), 0)} "
                    f"{'menos' if g04 < g1014 else 'más'} niños de 0 a 4 años que de 10 a 14", warn=True)
            anios_5 = [a for a in range(Y1 - 4, Y1 + 1)]
            if set(anios_5) <= set(ANIOS):
                n5 = int(serie[serie["anio"].isin(anios_5)]["nacimientos"].sum())
                dif5 = (g04 / n5 - 1) * 100
                nota(f"Control de coherencia: los nacimientos de {anios_5[0]}–{Y1} suman {fmt(n5)} y el grupo de 0 a 4 años "
                    f"es de {fmt(g04)} ({fpct(dif5, signo=True)} de diferencia). Los datos de nacimientos y de población son consistentes entre sí.")
            nota("La pirámide es de un solo momento (agosto 2024, solo nacionalidad y nacimiento argentinos): muestra la estructura actual, "
                "no cómo cambió. El efecto de largo plazo sobre el envejecimiento también depende de mortalidad y migración.")
            fuente("RENAPER, población identificada por provincia (agosto 2024).")

    
    
    #capitulo 8
    capitulo("c8", "08 · ¿QUÉ NOS CUENTA LA EVIDENCIA?", "Conclusiones descriptivas y fuentes")
    concl = [
        f"Entre {YP} y {Y1}, los nacimientos registrados {sube_baja(NP, N1)} aproximadamente {fpct(abs(CAIDA_PICO))}.",
    ]
    if fila_peor is not None:
        concl.append(f"La mayor variación anual fue en {int(fila_peor['anio'])} ({fpct(fila_peor['var_pct'], signo=True)}).")
    concl.append("Los mapas y el ranking provincial muestran que el fenómeno no es uniforme en el territorio.")
    if share is not None:
        concl.append(f"La proporción de nacimientos de madres menores de 20 años pasó de {fpct(share[y_a])} a {fpct(share[y_b])}.")
    tarjeta(bullets=concl)


    tarjeta("Fuentes estadísticas", bullets=[
            "DEIS / Ministerio de Salud: nacidos vivos registrados por año y provincia.",
            "RENAPER: población identificada por provincia (agosto 2024).",
            "INDEC: inflación y estimaciones de población.",
            "Presupuesto nacional: inversión en salud e investigación (datos.gob.ar).",
    ])

    st.markdown(
        f"""
    <div class="closing">
    <div class="kicker" style="margin-top:0">CIERRE</div>
    <h2>Argentina registra menos nacimientos que hace una década.</h2>
    <p>De {fmt(NP)} en {YP} a {fmt(N1)} en {Y1}: una variación de {fpct(CAIDA_PICO, signo=True)}.</p>
    <p>La cifra marca una transformación demográfica. Entender sus causas, sus diferencias territoriales y sus
    consecuencias requiere seguir investigando con datos comparables y fuentes verificables.</p>
    <p class="q">Pregunta para el debate: ¿qué políticas y servicios deberían adaptarse a una Argentina con menos nacimientos?</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.caption("Datos: datos.gob.ar · DEIS · RENAPER · INDEC.")


elif st.session_state.ver_general:
    
    #datos generaloes
    st.markdown("### 📊 Vista General de Todos los Años - Estadísticas Poblacionales")

    df_total_anio = df_agrupado.groupby("anio", as_index=False)["nacimientos"].sum()
    fig_total_anio = px.line(df_total_anio, x="anio", y="nacimientos", title="Evolución Total de Nacimientos en Argentina (2012-2024)", markers=True, template="plotly_dark", color_discrete_sequence=["#29b5e8"])
    fig_total_anio.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=400)
    st.plotly_chart(fig_total_anio, use_container_width=True)
    st.caption("Gráfico 1.1: Tendencia general de la natalidad a nivel nacional, evidenciando el punto de inflexión y posterior descenso sostenido.")

    fig_provincias_anio = px.line(df_agrupado, x="anio", y="nacimientos", color="provincia", title="Evolución Histórica de Nacimientos por Provincia", markers=True, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Prism)
    fig_provincias_anio.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=700)
    st.plotly_chart(fig_provincias_anio, use_container_width=True)
    st.caption("Gráfico 1.2: Desglose histórico plurianual por jurisdicción para contrastar la heterogeneidad territorial en los patrones de natalidad.")

    #distribucion x volumen de nacimiento
    st.markdown("### 🗺️ Distribución Relativa del Volumen de Nacimientos")
    top_provincias_acum = df_agrupado[df_agrupado['anio'] == df_agrupado['anio'].max()].sort_values(by="nacimientos", ascending=False).head(10)
    fig_top_bar = px.bar(top_provincias_acum, x="provincia", y="nacimientos", title=f"Provincias con Mayor Volumen de Nacimientos ({df_agrupado['anio'].max()})", template="plotly_dark", color="nacimientos", color_continuous_scale="Viridis")
    fig_top_bar.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=400)
    st.plotly_chart(fig_top_bar, use_container_width=True)
    st.caption("Gráfico 1.3: Concentración de los nacimientos en las principales jurisdicciones del país para el último período censado o registrado.")

    st.divider()
    st.markdown("### 💰 Análisis Económico: Inflación Anual vs. Salario Mínimo de Diciembre")

    try:
        #dfs
        df_salario = pd.read_csv('DATA_PROCESADA/ECONOMIA/salario_min_desde_2012.csv')
        df_inflacion = pd.read_csv('DATA_PROCESADA/ECONOMIA/inflacion_2012_2024.csv')
        df_var_inflacion = pd.read_csv('DATA_PROCESADA/ECONOMIA/variacion_inflacion_2012_2024.csv')

        
        if 'indice_tiempo' in df_salario.columns:
            df_salario['indice_tiempo'] = pd.to_datetime(df_salario['indice_tiempo'])
            df_salario_dic = df_salario[df_salario['indice_tiempo'].dt.month == 12].copy()
            df_salario_dic['anio'] = df_salario_dic['indice_tiempo'].dt.year
        elif 'fecha' in df_salario.columns:
            df_salario['fecha'] = pd.to_datetime(df_salario['fecha'])
            df_salario_dic = df_salario[df_salario['fecha'].dt.month == 12].copy()
            df_salario_dic['anio'] = df_salario_dic['fecha'].dt.year

        df_var_inflacion['anio'] = pd.to_numeric(df_var_inflacion['fecha'], errors='coerce')
        df_eco = pd.merge(df_salario_dic, df_var_inflacion, on='anio', how='inner')

        if not df_eco.empty:
            fig_eco = make_subplots(specs=[[{"secondary_y": True}]])

            fig_eco.add_trace(
                go.Scatter(
                    x=df_eco['anio'], 
                    y=df_eco['salario_minimo_vital_movil_mensual'], 
                    name="Salario Mínimo Mensual (Diciembre)",
                    line=dict(color="#3BB8A6", width=3)
                ),
                secondary_y=False,
            )
            
            col_var = 'variacion' if 'variacion' in df_eco.columns else df_eco.columns[-1]
            fig_eco.add_trace(
                go.Bar(
                    x=df_eco['anio'], 
                    y=df_eco[col_var], 
                    name="Variación Inflación Anual (%)",
                    marker_color="rgba(232, 96, 95, 0.6)"
                ),
                secondary_y=True,
            )

            fig_eco.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title="Comparativa: Salario Mínimo de Diciembre vs. Variación de Inflación Anual",
                height=550,
                legend=dict(orientation="h", y=1.15, x=0)
            )
            
            fig_eco.update_yaxes(title_text="<b>Salario Mínimo ($)</b>", secondary_y=False, gridcolor="#22345a")
            fig_eco.update_yaxes(title_text="<b>Variación Inflación (%)</b>", secondary_y=True, showgrid=False)

            st.plotly_chart(fig_eco, use_container_width=True)
            st.caption("Gráfico 1.4: Evolución cruzada entre los ajustes del salario mínimo nominal de diciembre y las fluctuaciones de la variación inflacionaria interanual.")
        else:
            st.info("No se encontraron registros coincidentes para unificar los datos económicos procesados.")

    except Exception as e:
        st.warning(f"No se pudieron cargar los archivos desde 'DATA_PROCESADA/ECONOMIA/'. Detalle: {e}")

    #grupo etario
    try:
        df_madres_gral = pd.read_csv("DATA_PROCESADA/POBLACION/madres_grupo_edad_total.csv")
        if df_madres_gral is not None and not df_madres_gral.empty:
            st.divider()
            st.markdown("### 👶 Composición Agregada de Nacimientos por Grupo Etario de la Madre")
            df_pivot_edad = df_madres_gral.pivot_table(index="anio", columns="grupo_etario_madre", values="cantidad", aggfunc="sum").reset_index()
            
            fig_area_edad = px.area(
                df_pivot_edad, 
                x="anio", 
                y=[c for c in df_pivot_edad.columns if c != "anio"], 
                title="Evolución de Nacimientos según Grupos Etarios Maternos (Acumulado)",
                template="plotly_dark"
            )
            fig_area_edad.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=450)
            st.plotly_chart(fig_area_edad, use_container_width=True)
            st.caption("Gráfico 1.5: Distribución en áreas apiladas que muestra el peso relativo de cada franja etaria de las madres en la caída global de los nacimientos.")
    except Exception:
        pass

else:
   pass
    

    
