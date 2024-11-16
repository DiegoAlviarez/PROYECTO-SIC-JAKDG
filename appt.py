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

# Cargar datos
@st.cache_data
def load_data():
    file_path = 'https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_actualizados%20(3).csv'
    return pd.read_csv(file_path)

# Función para convertir valores de mercado
def convertir_valor(valor):
    if isinstance(valor, str):
        if "mil €" in valor:
            return int(float(valor.replace(" mil €", "").replace(",", ".")) * 1_000)
        elif "mill. €" in valor:
            return int(float(valor.replace(" mill. €", "").replace(",", ".")) * 1_000_000)
    return None

# Cargar y preparar datos
data = load_data()
data["Valor de Mercado en 01/01/2024"] = data["Valor de Mercado en 01/01/2024"].apply(convertir_valor)
data["Valor de Mercado Actual"] = data["Valor de Mercado Actual"].apply(convertir_valor)

# Sidebar con menú principal
st.sidebar.title("Menú Principal")
menu_principal = st.sidebar.radio(
    "Seleccione una sección:",
    ["Introducción", "Objetivos", "Metodología", "Herramientas", "Resultados", "Conclusiones"]
)

# Contenido según la selección del menú
if menu_principal == "Introducción":
    st.title("Introducción")
    st.write("""
    La industria del fútbol ha evolucionado significativamente, convirtiéndose en un mercado 
    donde el valor de los jugadores es un indicador crucial de su desempeño y potencial.
    """)
    
    # Mostrar animación Lottie
    lottie_url = "https://lottie.host/embed/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        st_lottie(lottie_coding, height=200, width=300)
    
    # Mostrar tabla de jugadores
    st.subheader("Tabla de Jugadores")
    st.dataframe(data)

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
    
    # Submenu para visualizaciones
    visualizacion = st.selectbox(
        "Seleccione tipo de visualización:",
        ["Evolución Individual", "Comparación entre Jugadores", "Tendencias Generales"]
    )
    
    if visualizacion == "Evolución Individual":
        st.subheader("Evolución Individual del Valor de Mercado")
        nombre_jugador = st.selectbox("Selecciona un jugador:", data['Nombre'].unique())
        
        jugador = data[data['Nombre'] == nombre_jugador]
        if not jugador.empty:
            # Crear gráfica de evolución individual
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Enero 2024', 'Actual'],
                y=[jugador['Valor de Mercado en 01/01/2024'].iloc[0], 
                   jugador['Valor de Mercado Actual'].iloc[0]],
                name=nombre_jugador
            ))
            fig.update_layout(
                title=f'Evolución del Valor de Mercado de {nombre_jugador}',
                xaxis_title='Fecha',
                yaxis_title='Valor de Mercado (€)'
            )
            st.plotly_chart(fig)
            
    elif visualizacion == "Comparación entre Jugadores":
        st.subheader("Comparación entre Jugadores")
        col1, col2 = st.columns(2)
        with col1:
            jugador1 = st.selectbox("Primer jugador:", data['Nombre'].unique())
        with col2:
            jugador2 = st.selectbox("Segundo jugador:", data['Nombre'].unique())
        
        if jugador1 and jugador2:
            jugadores_data = data[data['Nombre'].isin([jugador1, jugador2])]
            
            # Crear gráfica de comparación
            fig = go.Figure()
            for jugador in [jugador1, jugador2]:
                datos_jugador = jugadores_data[jugadores_data['Nombre'] == jugador]
                fig.add_trace(go.Bar(
                    name=jugador,
                    x=['Enero 2024', 'Actual'],
                    y=[datos_jugador['Valor de Mercado en 01/01/2024'].iloc[0],
                       datos_jugador['Valor de Mercado Actual'].iloc[0]]
                ))
            
            fig.update_layout(
                title='Comparación de Valores de Mercado',
                barmode='group',
                xaxis_title='Fecha',
                yaxis_title='Valor de Mercado (€)'
            )
            st.plotly_chart(fig)
    
    elif visualizacion == "Tendencias Generales":
        st.subheader("Tendencias Generales del Mercado")
        
        # Crear gráfica de tendencias generales
        fig = go.Figure()
        for _, jugador in data.iterrows():
            fig.add_trace(go.Scatter(
                x=['Enero 2024', 'Actual'],
                y=[jugador['Valor de Mercado en 01/01/2024'],
                   jugador['Valor de Mercado Actual']],
                name=jugador['Nombre'],
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title='Tendencias Generales del Valor de Mercado',
            xaxis_title='Fecha',
            yaxis_title='Valor de Mercado (€)',
            showlegend=True
        )
        st.plotly_chart(fig)

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
        # Mostrar estadísticas descriptivas
        st.write("Estadísticas descriptivas de los valores de mercado:")
        st.dataframe(data[['Valor de Mercado en 01/01/2024', 'Valor de Mercado Actual']].describe())
        
    with tab2:
        st.header("Análisis de Tendencias")
        # Mostrar gráfico de tendencias
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=data['Valor de Mercado en 01/01/2024'],
            name='Enero 2024'
        ))
        fig.add_trace(go.Box(
            y=data['Valor de Mercado Actual'],
            name='Actual'
        ))
        fig.update_layout(
            title='Distribución de Valores de Mercado',
            yaxis_title='Valor de Mercado (€)'
        )
        st.plotly_chart(fig)
        
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
