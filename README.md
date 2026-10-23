# 🇦🇷 Dashboard de Natalidad en Argentina

Este proyecto es una aplicación web interactiva desarrollada con **Streamlit** para el análisis visual y la exploración de las estadísticas de natalidad en la República Argentina durante el período 2012–2024.

Permite consultar la evolución de nacimientos por provincia, analizar tendencias anuales y comparar datos socioeconómicos mediante visualizaciones dinámicas.

---

## 📊 Características Principales

* **Métricas de Variación Anual:** Identificación de las provincias con mayor aumento o disminución de nacimientos en comparación con el año anterior.
* **Tendencia Provincial:** Gráficos en formato de dona que representan el porcentaje de provincias en alza o a la baja en la tasa de nacimientos.
* **Distribución Geográfica y Ranking:** 
  * Gráficos de barras interactivos creados con Plotly.
  * Tabla interactiva con barra de progreso que destaca las provincias con mayor volumen de nacimientos.
* **Mapa de Calor Histórico:** Visualización temporal matricial (provincias vs. años) mediante Altair para detectar patrones históricos globales.
* **Personalización Visual:**
  * Paleta de colores configurable desde el panel lateral.
  * Diseño con efecto *Glassmorphism* mediante estilos CSS personalizados.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.8+**
* **Streamlit:** Framework principal para la interfaz interactiva.
* **Pandas:** Procesamiento, agrupación y limpieza de datasets.
* **Altair:** Gráficos estadísticos (mapa de calor y gráficos de dona).
* **Plotly Express:** Gráficos de barras interactivos.
* **Matplotlib:** Análisis exploratorio preliminar.

---

## 📁 Estructura del Proyecto

```text
.
├── DATA/
│   ├── ECONOMIA/         # Datos sobre economia
│   ├── POBLACION/        # Datos sobre poblacion
│   └── SALUD/            # Datos sobre salud
├── DATA_PROCESADA/
│   ├── ECONOMIA/
│   ├──POBLACION/
│   └── SALUD/
├── app.py                # Aplicación principal de Streamlit
├── economia.ipynb        # Analisis sobre datos de economia
├── inversion_salud.ipynb # Analisis sobre datos de salud
├── poblacion.ipynb       # Analisis sobre datos de poblacion
├── README.md             # Documentación del proyecto
└── requirements.txt      # Dependencias del proyecto
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/natalidad-argentina.git
cd natalidad-argentina
```

### 2. Crear y activar un entorno virtual (Opcional pero recomendado)
* **En Linux/macOS:**
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```
* **En Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 💻 Ejecución de la Aplicación

Para iniciar la interfaz interactiva con Streamlit, ejecuta:

```bash
streamlit run app_2.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`.

---

## 📑 Fuente de Datos

Los datos utilizados corresponden a estadísticas oficiales publicadas en los portales de datos abiertos de la República Argentina.

datos.gob.ar