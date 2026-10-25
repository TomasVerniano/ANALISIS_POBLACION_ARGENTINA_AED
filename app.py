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


if "ver_general" not in st.session_state:
  st.session_state.ver_general = False

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

  #logica de la barra del costado
  if st.session_state.ver_storytelling:
    if st.button("⬅ Volver al Dashboard", use_container_width=True):
      st.session_state.ver_storytelling = False
      st.session_state.ver_general = False
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
      st.rerun()

  else:
    if st.button("Ver Avance General", use_container_width=True):
      st.session_state.ver_general = True
      st.session_state.ver_storytelling = False
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
      st.rerun()

  #ocultar fondo
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
  if st.session_state.ver_storytelling or st.session_state.ver_general:
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
[data-testid="block-container"] {{
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}}

[data-testid="stAppViewContainer"] {{
    {background_style}
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    color: #ffffff !important;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

div[data-testid="stVerticalBlock"] > div[dir="ltr"] > div {{
    background: rgba(255, 255, 255, 0.12) !important;
    backdrop-filter: blur(12px) saturate(180%);
    -webkit-backdrop-filter: blur(12px) saturate(180%);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    padding: 20px;
    margin-bottom: 15px;
}}

.stButton>button {{
    background: rgba(255, 255, 255, 0.15) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 8px !important;
    backdrop-filter: blur(4px);
    transition: all 0.3s ease;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
}}

.stTextInput>div>div>input, .stSelectbox>div>div>div {{
    background: rgba(0, 0, 0, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 6px !important;
}}

h1, h2, h3, h4, h5, h6, p, label {{
    color: #ffffff !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}}
</style>
"""

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


if not st.session_state.ver_general:
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





#pestañás
  
    #storytelling
if st.session_state.ver_storytelling:
    # ──────────────────────────────────────────────────────────────
    # PÁGINA DE STORYTELLING
    # ──────────────────────────────────────────────────────────────
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

    # Portada Storytelling
    st.markdown('<div id="inicio"></div>', unsafe_allow_html=True)
    chips = "".join(f'<span class="chip">{a}</span>' for a in sorted({Y0, YP, Y1}))
    st.markdown(
        f"""
        <div class="hero">
        <h1>ARGENTINA:<br>UNA NATALIDAD EN TRANSFORMACIÓN</h1>
        <div class="sub">Una historia contada a través de los nacimientos registrados</div>
        <div class="meta">Storytelling demográfico · Análisis de la natalidad {Y0}–{Y1}</div>
        {chips}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Fuentes principales: Estadísticas Vitales (DEIS · Ministerio de Salud), datos abiertos de datos.gob.ar.")

    # Capítulo 1
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

    # Capítulo 2
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

    # Capítulo 3
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

    # Capítulo 4
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

    # Capítulo 5
    capitulo("c5", "05 · EDAD DE LAS MADRES", "¿Cuánto pesa la maternidad adolescente?")
    df_m = leer_csv("POBLACION", "madres_grupo_edad_total.csv")
    if df_m is not None:
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
            mostrar(dona_st(share[y_a], TEAL, str(y_a), 260), key="m_a")
        with cB:
            mostrar(dona_st(share[y_b], CORAL, str(y_b), 260), key="m_b")
        with cC:
            f = go.Figure(go.Scatter(x=share.index, y=share.values, mode="lines+markers", line=dict(color=YELLOW, width=4)))
            f.update_layout(title="% de nacimientos de madres menores de 20 años")
            mostrar(estilo(f, 260))

    # Conclusión final del Storytelling
    capitulo("c8", "08 · CONCLUSIONES", "Conclusiones descriptivas y fuentes")
    tarjeta(bullets=[f"Entre {YP} y {Y1}, los nacimientos registrados {sube_baja(NP, N1)} aproximadamente {fpct(abs(CAIDA_PICO))}."])
    st.markdown(
        f"""
        <div class="closing">
        <div class="kicker" style="margin-top:0">CIERRE</div>
        <h2>Argentina registra menos nacimientos que hace una década.</h2>
        <p>De {fmt(NP)} en {YP} a {fmt(N1)} en {Y1}: una variación de {fpct(CAIDA_PICO, signo=True)}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif st.session_state.ver_general:
    # ──────────────────────────────────────────────────────────────
    # VISTA GENERAL
    # ──────────────────────────────────────────────────────────────
    st.markdown("### 📊 Vista General de Todos los Años - Estadísticas Poblacionales")

    df_total_anio = df_agrupado.groupby("anio", as_index=False)["nacimientos"].sum()
    fig_total_anio = px.line(df_total_anio, x="anio", y="nacimientos", title="Evolución Total de Nacimientos en Argentina (2012-2024)", markers=True, template="plotly_dark", color_discrete_sequence=["#29b5e8"])
    fig_total_anio.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=400)
    st.plotly_chart(fig_total_anio, use_container_width=True)

    fig_provincias_anio = px.line(df_agrupado, x="anio", y="nacimientos", color="provincia", title="Evolución Histórica de Nacimientos por Provincia", markers=True, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Prism)
    fig_provincias_anio.update_layout(plot_bgcolor="rgba(0, 0, 0, 0)", paper_bgcolor="rgba(0, 0, 0, 0)", height=550)
    st.plotly_chart(fig_provincias_anio, use_container_width=True)

else:
    pass