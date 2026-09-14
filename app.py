import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("DATA_PROCESADA/cambios_genero_año_total.csv")

fig = plt.figure(figsize=(10,5))

plt.bar(data, color='maroon', height=1)
plt.xlabel('Cantidad')
plt.ylabel('Año')
plt.title('Cambios de genero totales por año hasta 2024')

st.pyplot(fig)