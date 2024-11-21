import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis Futbolístico",
    page_icon="⚽",
    layout="wide"
)

# Función para cargar animaciones Lottie
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Cargar datos
@st.cache_data
def load_data():
    spain_data = pd.read_csv('https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_actualizados%20(3).csv')
    bundesliga_data = pd.read_csv('https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_bundesliga.csv')
    return spain_data, bundesliga_data

# Función para convertir valores de mercado
def convertir_valor(valor):
    if isinstance(valor, str):
        if "mil €" in valor:
            return int(float(valor.replace(" mil €", "").replace(",", ".")) * 1_000)
        elif "mill. €" in valor:
            return int(float(valor.replace(" mill. €", "").replace(",", ".")) * 1_000_000)
    return None

# Función para convertir URLs a imágenes
def convertir_urls_a_imagenes(df):
    df_copy = df.copy()
    for col in df_copy.columns:
        if df_copy[col].astype(str).str.startswith('http').any():
            df_copy[col] = df_copy[col].apply(lambda url: f'<img src="{url}" width="50">' if isinstance(url, str) and url.startswith('http') else url)
    return df_copy

# Cargar datos
spain_data, bundesliga_data = load_data()

# Renombrar columnas de la Bundesliga
bundesliga_data.rename(
    columns={"Valor de Mercado": "Valor de Mercado 01/11/2024", "Actual": "Valor de Mercado Actual"},
    inplace=True
)

# Procesar valores de mercado en ambos datasets
spain_data["Valor de Mercado en 01/01/2024"] = spain_data["Valor de Mercado en 01/01/2024"].apply(convertir_valor)
spain_data["Valor de Mercado Actual"] = spain_data["Valor de Mercado Actual"].apply(convertir_valor)
bundesliga_data["Valor de Mercado 01/11/2024"] = bundesliga_data["Valor de Mercado 01/11/2024"].apply(convertir_valor)
bundesliga_data["Valor de Mercado Actual"] = bundesliga_data["Valor de Mercado Actual"].apply(convertir_valor)

# Sidebar con menú principal
st.sidebar.title("Menú Principal")
menu_principal = st.sidebar.radio(
    "Seleccione una sección:",
    ["Introducción", "Comparativa", "Gráficos", "Conclusión"]
)

# Selector de liga
liga_seleccionada = st.sidebar.selectbox(
    "Seleccione la liga:",
    ["LaLiga", "Bundesliga", "Comparativa"]
)

if menu_principal == "Introducción":
    st.title("Introducción")
    st.write("""
    La industria del fútbol ha evolucionado significativamente, convirtiéndose en un mercado 
    donde el valor de los jugadores es un indicador crucial de su desempeño y potencial.
    """)
    
    lottie_url = "https://lottie.host/embed/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        st_lottie(lottie_coding, height=200, width=300)

    if liga_seleccionada == "LaLiga":
        data_to_show = spain_data
        title = "Datos de Jugadores de LaLiga"
    elif liga_seleccionada == "Bundesliga":
        data_to_show = bundesliga_data
        title = "Datos de Jugadores de Bundesliga"
    else:
        st.subheader("Comparativa entre LaLiga y Bundesliga")
        col1, col2 = st.columns(2)
        with col1:
            st.write("### LaLiga")
            st.dataframe(convertir_urls_a_imagenes(spain_data).to_html(escape=False), unsafe_allow_html=True)
        with col2:
            st.write("### Bundesliga")
            st.dataframe(convertir_urls_a_imagenes(bundesliga_data).to_html(escape=False), unsafe_allow_html=True)
        
    if liga_seleccionada != "Comparativa":
        with st.container():
            st.subheader(title)
            data_con_imagenes = convertir_urls_a_imagenes(data_to_show)
            st.markdown(data_con_imagenes.to_html(escape=False), unsafe_allow_html=True)

elif menu_principal == "Comparativa":
    st.title("Comparativa de Ligas")
    st.write("""
    Compare los valores de mercado de jugadores entre LaLiga y Bundesliga.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos de LaLiga")
        st.dataframe(spain_data)
    with col2:
        st.subheader("Datos de Bundesliga")
        st.dataframe(bundesliga_data)

elif menu_principal == "Gráficos":
    st.title("Gráficos Comparativos")
    st.write("""
    Visualice las diferencias en el valor de mercado entre jugadores de las distintas ligas.
    """)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=spain_data["Jugador"],
        y=spain_data["Valor de Mercado Actual"],
        name="LaLiga",
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=bundesliga_data["Jugador"],
        y=bundesliga_data["Valor de Mercado Actual"],
        name="Bundesliga",
        marker_color='red'
    ))
    fig.update_layout(
        title="Comparación de Valores de Mercado",
        xaxis_title="Jugadores",
        yaxis_title="Valor de Mercado (€)",
        barmode='group'
    )
    st.plotly_chart(fig)

elif menu_principal == "Conclusión":
    st.title("Conclusión")
    st.write("""
    A través del análisis realizado, podemos observar las diferencias significativas entre las ligas 
    en términos de valor de mercado, lo que refleja las dinámicas únicas de cada competición.
    """)
    st.write("Gracias por explorar este análisis.")


# Footer
st.sidebar.markdown("---")
st.sidebar.info("ANÁLISIS DE LAS ESTADÍSTICAS QUE TIENEN MAYOR CORRELACIÓN CON EL VALOR DE MERCADO DE LOS JUGADORES DE FUTBOL EN ESPAÑA Y ALEMANIA")
