import pandas as pd
import streamlit as st

# Enlace directo al archivo raw en GitHub
file_path = 'https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_actualizados%20(3).csv'
data = pd.read_csv(file_path)

# Función para convertir URLs en imágenes en cualquier columna
def convertir_urls_a_imagenes(df):
    # Crear una copia para no modificar el DataFrame original
    df_copy = df.copy()
    
    # Identificar columnas que contienen URLs y convertirlas en HTML de imágenes
    for col in df_copy.columns:
        # Comprobar si la columna contiene URLs (esto asume que todas las filas de la columna contienen URLs si la primera fila lo tiene)
        if df_copy[col].astype(str).str.startswith('http').any():
            df_copy[col] = df_copy[col].apply(lambda url: f'<img src="{url}" width="50">' if isinstance(url, str) and url.startswith('http') else url)
    
    return df_copy

# Convertir las URLs en imágenes para la tabla
data_con_imagenes = convertir_urls_a_imagenes(data)

# Mostrar la tabla en Streamlit con las imágenes renderizadas
with st.container():
    st.subheader("Datos de Jugadores")
    st.write("Tabla completa con imágenes de los jugadores y valores de mercado.")
    # Renderizar la tabla con HTML para mostrar las imágenes
    st.markdown(data_con_imagenes.to_html(escape=False), unsafe_allow_html=True)


