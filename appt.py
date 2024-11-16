import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
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

# Sidebar con menú principal
st.sidebar.title("Menú Principal")
menu_principal = st.sidebar.radio(
    "Seleccione una sección:",
    ["Introducción", "Objetivos", "Metodología", "Herramientas", "Resultados", "Conclusiones"]
)

# Cargar datos
@st.cache_data
def load_data():
    file_path = 'https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_actualizados%20(3).csv'
    return pd.read_csv(file_path)

data = load_data()

# Función para convertir valores de mercado
def convertir_valor(valor):
    if isinstance(valor, str):
        if "mil €" in valor:
            return int(float(valor.replace(" mil €", "").replace(",", ".")) * 1_000)
        elif "mill. €" in valor:
            return int(float(valor.replace(" mill. €", "").replace(",", ".")) * 1_000_000)
    return None

# Contenido según la selección del menú
if menu_principal == "Introducción":
    st.title("Introducción")
    st.write("""
    La industria del fútbol ha evolucionado significativamente, convirtiéndose en un mercado 
    donde el valor de los jugadores es un indicador crucial de su desempeño y potencial.
    
    Este proyecto se centra en el análisis de datos de jugadores de la liga 2024, utilizando 
    información detallada sobre el valor de mercado de cada jugador.
    """)
    
    # Mostrar animación Lottie en la introducción
    lottie_url = "https://lottie.host/embed/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        st_lottie(lottie_coding, height=200, width=300)

elif menu_principal == "Objetivos":
    st.title("Objetivos del Proyecto")
    st.write("""
    ### Objetivos Principales:
    - Analizar y visualizar el valor de mercado de los jugadores
    - Evaluar el incremento porcentual del valor de mercado a lo largo del tiempo
    - Identificar patrones y tendencias en la valoración de jugadores
    """)

elif menu_principal == "Metodología":
    st.title("Metodología")
    
    st.header("Recolección de Datos")
    st.write("""
    - Utilización de archivo CSV con datos actualizados
    - Información incluye: nombre, posición, nacionalidad, edad, equipo y valores de mercado
    """)
    
    st.header("Análisis de Datos")
    st.write("""
    - Carga y procesamiento con pandas
    - Limpieza y validación de datos
    - Análisis estadístico descriptivo
    """)
    
    # Submenu para visualizaciones
    visualizacion = st.selectbox(
        "Seleccione tipo de visualización:",
        ["Evolución Individual", "Comparación entre Jugadores", "Tendencias Generales"]
    )
    
    if visualizacion == "Evolución Individual":
        nombre_jugador = st.selectbox("Selecciona un jugador:", data['Nombre'].unique())
        # Aquí va tu código existente para la gráfica individual
        
    elif visualizacion == "Comparación entre Jugadores":
        st.write("Seleccione dos jugadores para comparar:")
        jugador1 = st.selectbox("Primer jugador:", data['Nombre'].unique())
        jugador2 = st.selectbox("Segundo jugador:", data['Nombre'].unique())
        # Aquí va tu código existente para la comparación

elif menu_principal == "Herramientas":
    st.title("Herramientas y Tecnologías")
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Tecnologías Principales")
        st.write("""
        - Python
        - Pandas
        - Streamlit
        - Plotly
        """)
    
    with col2:
        st.header("Bibliotecas Adicionales")
        st.write("""
        - Matplotlib
        - Seaborn
        - Streamlit-Lottie
        """)

elif menu_principal == "Resultados":
    st.title("Resultados")
    
    tab1, tab2, tab3 = st.tabs(["Estadísticas Generales", "Análisis de Tendencias", "Recomendaciones"])
    
    with tab1:
        st.header("Estadísticas Generales")
        # Aquí puedes mostrar tus gráficas existentes
        
    with tab2:
        st.header("Análisis de Tendencias")
        # Código para mostrar tendencias
        
    with tab3:
        st.header("Recomendaciones")
        st.write("""
        Basadas en el análisis de datos:
        - Recomendaciones para clubes
        - Estrategias de inversión
        - Oportunidades de mercado
        """)

else:  # Conclusiones
    st.title("Conclusiones")
    st.write("""
    ### Principales Hallazgos:
    - El análisis de datos en el fútbol ofrece insights valiosos para la toma de decisiones
    - Las tendencias del mercado muestran patrones significativos en la valoración de jugadores
    - La gestión basada en datos puede mejorar significativamente las estrategias de los equipos
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Desarrollado con ❤️ usando Streamlit")
