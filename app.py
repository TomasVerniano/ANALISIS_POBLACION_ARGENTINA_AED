import streamlit as st
import pandas as pd
import altair as alt
import plotly_express as px

#config de la pagina

st.set_page_config(
    page_title="Taza de Natalidad en la Argentina",
    page_icon="🇦🇷",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#markdown

st.markdown(
    """
    <style>
    [data-testid="block-container"] {
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 1rem;
        padding-bottom: 0rem;
        margin-bottom: -7rem;
    }

    .stApp {
        background: linear-gradient(#b155ff, #1e3c72 0%, #831b92 100%, #b155ff 50%);
        background-attachment: fixed;
        color: #ffffff !important;
    }

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

    .stButton>button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.5);
    }

      .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 6px !important;
    }

    h1, h2, h3, h4, h5, h6, p, label {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    </style>

    """, unsafe_allow_html=True)

#cargamps los datos
@st.cache_data
def cargar_datos():
    df_madres = pd.read_csv('DATA\POBLACION\cantidad_de_nacimientos_edad_madre_por_anio_de_nacimiento_2012_2024.csv')
    df_agrupado = df_madres.groupby(['provincia_nombre', 'provincia_id', 'anio'], as_index=False)['cantidad'].sum()
    df_agrupado = df_agrupado.rename(columns={
        'provincia_nombre': 'provincia',
        'provincia_id': 'id_provincia',
        'anio': 'anio',
        'cantidad': 'nacimientos'
    })
    df_agrupado['codigo_provincia'] = df_agrupado['id_provincia'].astype(str)
    return df_agrupado

df_agrupado = cargar_datos()


#barra del costado
with st.sidebar:
    st.title('🇦🇷 Dashboard de Natalidad')
    
    lista_anios = list(df_agrupado.anio.unique())[::-1]
    
    anio_seleccionado = st.selectbox('Seleccione un año', lista_anios)
    df_anio_seleccionado = df_agrupado[df_agrupado.anio == anio_seleccionado]
    df_anio_ordenado = df_anio_seleccionado.sort_values(by="nacimientos", ascending=False)

    lista_temas_color = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    tema_color_seleccionado = st.selectbox('Seleccione un color', lista_temas_color)


#graficos

#mapa de calor
def crear_mapa_calor(df_entrada, eje_y, eje_x, columna_color, esquema_color):
    mapa_calor = alt.Chart(df_entrada).mark_rect().encode(
            y=alt.Y(f'{eje_y}:O', axis=alt.Axis(title="Año", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{eje_x}:O', axis=alt.Axis(title="Provincia", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=-45)),
            color=alt.Color(f'max({columna_color}):Q',
                           legend=None,
                           scale=alt.Scale(scheme=esquema_color)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900, height=400
        ).configure_axis(
        labelFontSize=11,
        titleFontSize=12
        ) 
    return mapa_calor

#grafico de barras
def crear_grafico_barras(df_entrada, eje_x, eje_y, esquema_color):
    grafico = px.bar(
        df_entrada, 
        x=eje_x, 
        y=eje_y, 
        color=eje_x,
        color_discrete_sequence=px.colors.qualitative.Prism,
        template='plotly_dark'
    )
    grafico.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350,
        showlegend=False
    )
    return grafico

#dona
def crear_grafico_dona(valor_porcentaje, texto_etiqueta, color_tema):
    if color_tema == 'blue':
        colores_grafico = ['#29b5e8', '#155F7A']
    elif color_tema == 'green':
        colores_grafico = ['#27AE60', '#12783D']
    elif color_tema == 'orange':
        colores_grafico = ['#F39C12', '#875A12']
    elif color_tema == 'red':
        colores_grafico = ['#E74C3C', '#781F16']
    else:
        colores_grafico = ['#29b5e8', '#155F7A']
        
    fuente_datos = pd.DataFrame({
        "Tema": ['', texto_etiqueta],
        "% valor": [100 - valor_porcentaje, valor_porcentaje]
    })
    fuente_datos_fondo = pd.DataFrame({
        "Tema": ['', texto_etiqueta],
        "% valor": [100, 0]
    })
        
    grafico = alt.Chart(fuente_datos).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% valor",
        color=alt.Color("Tema:N",
                        scale=alt.Scale(domain=[texto_etiqueta, ''], range=colores_grafico),
                        legend=None),
    ).properties(width=130, height=130)
        
    texto = grafico.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{valor_porcentaje} %'))
    grafico_fondo = alt.Chart(fuente_datos_fondo).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% valor",
        color=alt.Color("Tema:N",
                        scale=alt.Scale(domain=[texto_etiqueta, ''], range=colores_grafico),
                        legend=None),
    ).properties(width=130, height=130)
    return grafico_fondo + grafico + texto

#formato de los numeros
def formatear_numero(numero):
    if numero > 1000000:
        if not numero % 1000000:
            return f'{numero // 1000000} M'
        return f'{round(numero / 1000000, 1)} M'
    return f'{numero // 1000} K'

#diferencia de nacimientos año a año
def calcular_diferencia_nacimientos(df_entrada, anio_consulta):
    datos_anio_actual = df_entrada[df_entrada['anio'] == anio_consulta].reset_index(drop=True)
    datos_anio_anterior = df_entrada[df_entrada['anio'] == anio_consulta - 1].reset_index(drop=True)
    
    if not datos_anio_anterior.empty:
        datos_anio_actual['diferencia_nacimientos'] = datos_anio_actual.nacimientos.sub(datos_anio_anterior.nacimientos, fill_value=0)
    else:
        datos_anio_actual['diferencia_nacimientos'] = 0
        
    return pd.concat([datos_anio_actual.provincia, datos_anio_actual.id_provincia, datos_anio_actual.nacimientos, datos_anio_actual.diferencia_nacimientos], axis=1).sort_values(by="diferencia_nacimientos", ascending=False)


#panel principal
columnas = st.columns((1.5, 4.5, 2), gap='medium')

with columnas[0]:
    st.markdown('#### Variación Anual')

    anio_minimo = df_agrupado.anio.min()
    df_diferencia_ordenado = calcular_diferencia_nacimientos(df_agrupado, anio_seleccionado)

    if anio_seleccionado > anio_minimo:
        nombre_primera_provincia = df_diferencia_ordenado.provincia.iloc[0]
        nacimientos_primera_provincia = formatear_numero(df_diferencia_ordenado.nacimientos.iloc[0])
        variacion_primera_provincia = formatear_numero(df_diferencia_ordenado.diferencia_nacimientos.iloc[0])
    else:
        nombre_primera_provincia = '-'
        nacimientos_primera_provincia = '-'
        variacion_primera_provincia = ''
    st.metric(label=nombre_primera_provincia, value=nacimientos_primera_provincia, delta=variacion_primera_provincia)

    if anio_seleccionado > anio_minimo:
        nombre_ultima_provincia = df_diferencia_ordenado.provincia.iloc[-1]
        nacimientos_ultima_provincia = formatear_numero(df_diferencia_ordenado.nacimientos.iloc[-1])    
        variacion_ultima_provincia = formatear_numero(df_diferencia_ordenado.diferencia_nacimientos.iloc[-1])    
    else:
        nombre_ultima_provincia = '-'
        nacimientos_ultima_provincia = '-'
        variacion_ultima_provincia = ''
    st.metric(label=nombre_ultima_provincia, value=nacimientos_ultima_provincia, delta=variacion_ultima_provincia)

    st.markdown('#### Tendencia Provincial')

    if anio_seleccionado > anio_minimo:
        df_en_alza = df_diferencia_ordenado[df_diferencia_ordenado.diferencia_nacimientos > 0]
        df_a_la_baja = df_diferencia_ordenado[df_diferencia_ordenado.diferencia_nacimientos < 0]
        
        porcentaje_alza = round((len(df_en_alza) / df_diferencia_ordenado.provincia.nunique()) * 100)
        porcentaje_baja = round((len(df_a_la_baja) / df_diferencia_ordenado.provincia.nunique()) * 100)
        
        grafico_dona_alza = crear_grafico_dona(porcentaje_alza, 'En Alza', 'green')
        grafico_dona_baja = crear_grafico_dona(porcentaje_baja, 'A la Baja', 'red')
    else:
        grafico_dona_alza = crear_grafico_dona(0, 'En Alza', 'green')
        grafico_dona_baja = crear_grafico_dona(0, 'A la Baja', 'red')

    columnas_tendencia = st.columns((0.2, 1, 0.2))
    with columnas_tendencia[1]:
        st.write('En Alza')
        st.altair_chart(grafico_dona_alza)
        st.write('A la Baja')
        st.altair_chart(grafico_dona_baja)

with columnas[1]:
    st.markdown('#### Total de Nacimientos por Provincia')
    
    grafico_barras = crear_grafico_barras(df_anio_ordenado, 'provincia', 'nacimientos', tema_color_seleccionado)
    st.plotly_chart(grafico_barras, use_container_width=True)
    
    st.markdown('#### Mapa de Calor Histórico')
    mapa_calor = crear_mapa_calor(df_agrupado, 'anio', 'provincia', 'nacimientos', tema_color_seleccionado)
    st.altair_chart(mapa_calor, use_container_width=True)

with columnas[2]:
    st.markdown('#### Top Provincias')

    st.dataframe(df_anio_ordenado,
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
                     )}
                 )
    
    with st.expander('Acerca de', expanded=True):
        st.write("""
            - Datos: Estadísticas Vitales - Argentina.
            - :orange[**Variación Anual**]: Provincias con mayor aumento/disminución de nacimientos respecto al año previo.
            - :orange[**Tendencia Provincial**]: Porcentaje de provincias con variaciones positivas o negativas.
            """) 