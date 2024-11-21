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

# Función para generar valores mensuales interpolados
def generar_valores_mensuales(valor_inicial, valor_final):
    fecha_inicio = datetime(2024, 1, 1)
    fecha_actual = datetime.now()
    meses = []
    valores = []
    
    fecha_actual = fecha_actual.replace(day=1)
    fecha = fecha_inicio
    while fecha <= fecha_actual:
        meses.append(fecha.strftime('%B %Y'))
        fecha += timedelta(days=32)
        fecha = fecha.replace(day=1)
    
    num_meses = len(meses)
    for i in range(num_meses):
        valor = valor_inicial + (valor_final - valor_inicial) * (i / (num_meses - 1))
        valores.append(valor)
    
    return meses, valores

# Cargar datos
spain_data, bundesliga_data = load_data()

# Procesar datos de España
spain_data["Valor de Mercado en 01/01/2024"] = spain_data["Valor de Mercado en 01/01/2024"].apply(convertir_valor)
spain_data["Valor de Mercado Actual"] = spain_data["Valor de Mercado Actual"].apply(convertir_valor)

# Procesar datos de Bundesliga
bundesliga_data["Valor de Mercado en 01/01/2024"] = bundesliga_data["Valor de Mercado en 01/01/2024"].apply(convertir_valor)
bundesliga_data["Valor de Mercado Actual"] = bundesliga_data["Valor de Mercado Actual"].apply(convertir_valor)

# Sidebar con menú principal
st.sidebar.title("Menú Principal")
menu_principal = st.sidebar.radio(
    "Seleccione una sección:",
    ["Introducción", "Objetivos", "Metodología", "Herramientas", "Resultados", "Conclusiones"]
)

# Selector de liga
liga_seleccionada = st.sidebar.selectbox(
    "Seleccione la liga:",
    ["LaLiga", "Bundesliga", "Comparativa"]
)

# Función principal para cada sección del menú
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
            st.dataframe(spain_data)
        with col2:
            st.write("### Bundesliga")
            st.dataframe(bundesliga_data)
        
    if liga_seleccionada != "Comparativa":
        with st.container():
            st.subheader(title)
            data_con_imagenes = convertir_urls_a_imagenes(data_to_show)
            st.markdown(data_con_imagenes.to_html(escape=False), unsafe_allow_html=True)

elif menu_principal == "Metodología":
    st.title("Metodología")
    
    visualizacion = st.selectbox(
        "Seleccione tipo de visualización:",
        ["Evolución Individual", "Comparación entre Jugadores", "Tendencias Generales"]
    )
    
    if liga_seleccionada == "LaLiga":
        data = spain_data
    elif liga_seleccionada == "Bundesliga":
        data = bundesliga_data
    
    if visualizacion == "Evolución Individual":
        st.subheader(f"Evolución Individual del Valor de Mercado - {liga_seleccionada}")
        nombre_jugador = st.selectbox("Selecciona un jugador:", data['Nombre'].unique())
        
        jugador = data[data['Nombre'] == nombre_jugador]
        if not jugador.empty:
            valor_inicial = jugador['Valor de Mercado en 01/01/2024'].iloc[0]
            valor_final = jugador['Valor de Mercado Actual'].iloc[0]
            
            meses, valores = generar_valores_mensuales(valor_inicial, valor_final)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=meses,
                y=valores,
                mode='lines+markers',
                name=nombre_jugador,
                line=dict(width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title=f'Evolución Mensual del Valor de Mercado de {nombre_jugador}',
                xaxis_title='Mes',
                yaxis_title='Valor de Mercado (€)',
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig)

