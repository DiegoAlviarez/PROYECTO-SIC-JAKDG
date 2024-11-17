import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
from streamlit_particles import particles
import json
from utils import load_lottieurl, convertir_valor
from components import (
    crear_grafico_evolucion,
    mostrar_metricas_jugador,
    crear_grafico_comparacion
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis Futbolístico",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de partículas para el fondo
particles_config = {
    "particles": {
        "number": {
            "value": 30,
            "density": {
                "enable": True,
                "value_area": 800
            }
        },
        "color": {
            "value": "#ffffff"
        },
        "shape": {
            "type": "circle"
        },
        "opacity": {
            "value": 0.5,
            "random": False
        },
        "size": {
            "value": 3,
            "random": True
        },
        "line_linked": {
            "enable": True,
            "distance": 150,
            "color": "#ffffff",
            "opacity": 0.4,
            "width": 1
        },
        "move": {
            "enable": True,
            "speed": 2,
            "direction": "none",
            "random": False,
            "straight": False,
            "out_mode": "out",
            "bounce": False,
        }
    }
}

# Aplicar partículas al fondo
particles(particles_config, height="100vh")

# Cargar datos
@st.cache_data
def load_data():
    file_path = 'https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_actualizados%20(3).csv'
    df = pd.read_csv(file_path)
    df["Valor de Mercado en 01/01/2024"] = df["Valor de Mercado en 01/01/2024"].apply(convertir_valor)
    df["Valor de Mercado Actual"] = df["Valor de Mercado Actual"].apply(convertir_valor)
    return df

# Cargar datos
data = load_data()

# Sidebar con menú principal
with st.sidebar:
    st.title("⚽ Análisis Futbolístico")
    menu_principal = st.radio(
        "Navegación",
        ["📊 Dashboard", "📈 Análisis Individual", "🔄 Comparativa", "📋 Datos"],
        index=0
    )

# Contenido principal
if menu_principal == "📊 Dashboard":
    st.title("Dashboard Futbolístico Interactivo")
    
    # Animación Lottie
    lottie_url = "https://lottie.host/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st_lottie(lottie_coding, height=200)
    
    # Estadísticas generales
    st.subheader("📈 Estadísticas Generales")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        valor_total_inicial = data["Valor de Mercado en 01/01/2024"].sum()
        st.metric("Valor Total Inicial", f"€{valor_total_inicial:,.0f}")
    
    with col2:
        valor_total_actual = data["Valor de Mercado Actual"].sum()
        cambio_total = valor_total_actual - valor_total_inicial
        st.metric("Valor Total Actual", f"€{valor_total_actual:,.0f}", 
                 delta=f"€{cambio_total:,.0f}")
    
    with col3:
        cambio_porcentual = ((valor_total_actual - valor_total_inicial) / valor_total_inicial) * 100
        st.metric("Cambio Porcentual", f"{cambio_porcentual:.1f}%")

elif menu_principal == "📈 Análisis Individual":
    st.title("Análisis Individual de Jugadores")
    
    # Selector de jugador con búsqueda
    nombre_jugador = st.selectbox(
        "Selecciona un jugador:",
        data['Nombre'].unique(),
        index=0
    )
    
    if nombre_jugador:
        jugador_data = data[data['Nombre'] == nombre_jugador]
        
        # Mostrar métricas del jugador
        mostrar_metricas_jugador(jugador_data)
        
        # Gráfico de evolución
        fig = crear_grafico_evolucion(
            nombre_jugador,
            jugador_data['Valor de Mercado en 01/01/2024'].iloc[0],
            jugador_data['Valor de Mercado Actual'].iloc[0]
        )
        st.plotly_chart(fig, use_container_width=True)

elif menu_principal == "🔄 Comparativa":
    st.title("Comparativa entre Jugadores")
    
    col1, col2 = st.columns(2)
    with col1:
        jugador1 = st.selectbox("Primer jugador:", data['Nombre'].unique(), index=0)
    with col2:
        jugador2 = st.selectbox("Segundo jugador:", 
                               data[data['Nombre'] != jugador1]['Nombre'].unique(),
                               index=0)
    
    if jugador1 and jugador2:
        fig = crear_grafico_comparacion(data, [jugador1, jugador2])
        st.plotly_chart(fig, use_container_width=True)

else:  # Datos
    st.title("Datos Completos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        min_valor = st.number_input(
            "Valor mínimo (€)",
            min_value=0,
            max_value=int(data["Valor de Mercado Actual"].max()),
            value=0
        )
    with col2:
        max_valor = st.number_input(
            "Valor máximo (€)",
            min_value=0,
            max_value=int(data["Valor de Mercado Actual"].max()),
            value=int(data["Valor de Mercado Actual"].max())
        )
    
    # Filtrar datos
    filtered_data = data[
        (data["Valor de Mercado Actual"] >= min_valor) &
        (data["Valor de Mercado Actual"] <= max_valor)
    ]
    
    # Mostrar datos filtrados
    st.dataframe(
        filtered_data,
        column_config={
            "Valor de Mercado en 01/01/2024": st.column_config.NumberColumn(
                "Valor Inicial",
                format="€%.0f"
            ),
            "Valor de Mercado Actual": st.column_config.NumberColumn(
                "Valor Actual",
                format="€%.0f"
            )
        },
        hide_index=True
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "ANÁLISIS DE LAS ESTADÍSTICAS QUE TIENEN MAYOR CORRELACIÓN CON EL "
    "VALOR DE MERCADO DE LOS JUGADORES DE FUTBOL EN ESPAÑA"
)
