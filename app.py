#librerias
import base64
import os
import altair as alt
import numpy as np
import pandas as pd
import plotly_express as px
import requests
import streamlit as st

#ttulo
st.set_page_config(page_title="Dashboard de Natalidad", layout="wide")


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


#cargamos la figura del mapa de abajo
@st.cache_data
def cargar_geojson():
  url = "https://apis.datos.gob.ar/georef/api/v2.0/provincias.geojson"
  return requests.get(url).json()


geojson_arg = cargar_geojson()
nombres_provincias = [
    feature["properties"]["nombre"] for feature in geojson_arg["features"]
]


#barra del costado
with st.sidebar:
  st.title("🇦🇷 Dashboard de Natalidad")

  lista_anios = list(df_agrupado.anio.unique())[::-1]

  anio_seleccionado = st.selectbox("Seleccione un año", lista_anios)
  df_anio_seleccionado = df_agrupado[df_agrupado.anio == anio_seleccionado]
  df_anio_ordenado = df_anio_seleccionado.sort_values(
      by="nacimientos", ascending=False
  )
    #selector d color
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
  tema_color_seleccionado = st.selectbox(
      "Seleccione un color", lista_temas_color
  )



#convertir imagen local a url
def get_base64_img(file_path):
  if not os.path.exists(file_path):
    return ""
  with open(file_path, "rb") as f:
    data = f.read()
  return base64.b64encode(data).decode()


rutas_imagenes = {
    2012: "BACKGROUNDS\pj.png",
    2013: "BACKGROUNDS\pj.png",
    2014: "BACKGROUNDS\pj.png",
    2015: "BACKGROUNDS\pro.png",
    2016: "BACKGROUNDS\pro.png",
    2017: "BACKGROUNDS\pro.png",
    2018: "BACKGROUNDS\pro.png",
    2019: r"BACKGROUNDS\fdt.png",
    2020: r"BACKGROUNDS\fdt.png",
    2021: r"BACKGROUNDS\fdt.png",
    2022: r"BACKGROUNDS\fdt.png",
    2023: r"BACKGROUNDS\fdt.png",
    2024: "BACKGROUNDS\lla.png",
}

ruta_local = rutas_imagenes[anio_seleccionado]
base64_string = get_base64_img(ruta_local)

if base64_string:
  background_style = (
      f'background-image: url("data:image/jpeg;base64,{base64_string}");'
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
          y=alt.Y(
              f"{eje_y}:O",
              axis=alt.Axis(
                  title="Año",
                  titleFontSize=18,
                  titlePadding=15,
                  titleFontWeight=900,
                  labelAngle=0,
              ),
          ),
          x=alt.X(
              f"{eje_x}:O",
              axis=alt.Axis(
                  title="Provincia",
                  titleFontSize=18,
                  titlePadding=15,
                  titleFontWeight=900,
                  labelAngle=-45,
              ),
          ),
          color=alt.Color(
              f"max({columna_color}):Q",
              legend=None,
              scale=alt.Scale(scheme=esquema_color),
          ),
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

  fuente_datos = pd.DataFrame(
      {"Tema": ["", texto_etiqueta], "% valor": [100 - valor_porcentaje, valor_porcentaje]}
  )
  fuente_datos_fondo = pd.DataFrame(
      {"Tema": ["", texto_etiqueta], "% valor": [100, 0]}
  )

  grafico = (
      alt.Chart(fuente_datos)
      .mark_arc(innerRadius=45, cornerRadius=45)
      .encode(
          theta="% valor",
          color=alt.Color(
              "Tema:N",
              scale=alt.Scale(
                  domain=[texto_etiqueta, ""], range=colores_grafico
              ),
              legend=None,
          ),
      )
      .properties(width=130, height=130)
  )

  texto = grafico.mark_text(
      align="center",
      color="#29b5e8",
      font="Lato",
      fontSize=32,
      fontWeight=700,
      fontStyle="italic",
  ).encode(text=alt.value(f"{valor_porcentaje} %"))
  grafico_fondo = (
      alt.Chart(fuente_datos_fondo)
      .mark_arc(innerRadius=45, cornerRadius=20)
      .encode(
          theta="% valor",
          color=alt.Color(
              "Tema:N",
              scale=alt.Scale(
                  domain=[texto_etiqueta, ""], range=colores_grafico
              ),
              legend=None,
          ),
      )
      .properties(width=130, height=130)
  )

  grafico_final = (
      (grafico_fondo + grafico + texto)
      .configure_view(fill="black")
      .configure(background="transparent")
  )

  return grafico_final

#formato a los num
def formatear_numero(numero):
  if numero > 1000000:
    if not numero % 1000000:
      return f"{numero // 1000000} M"
    return f"{round(numero / 1000000, 1)} M"
  return f"{numero // 1000} K"


def calcular_diferencia_nacimientos(df_entrada, anio_consulta):
  datos_anio_actual = df_entrada[df_entrada["anio"] == anio_consulta].reset_index(
      drop=True
  )
  datos_anio_anterior = df_entrada[
      df_entrada["anio"] == anio_consulta - 1
  ].reset_index(drop=True)

  if not datos_anio_anterior.empty:
    datos_anio_actual["diferencia_nacimientos"] = (
        datos_anio_actual.nacimientos.sub(
            datos_anio_anterior.nacimientos, fill_value=0
        )
    )
  else:
    datos_anio_actual["diferencia_nacimientos"] = 0

  return (
      pd.concat(
          [
              datos_anio_actual.provincia,
              datos_anio_actual.nacimientos,
              datos_anio_actual.diferencia_nacimientos,
          ],
          axis=1,
      )
      .sort_values(by="diferencia_nacimientos", ascending=False)
  )


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