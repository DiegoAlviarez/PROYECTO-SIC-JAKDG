import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie
from utils import load_lottieurl, convertir_valor, convertir_urls_a_imagenes, generar_valores_mensuales, format_currency
from data_loader import DataLoader

# Configuración inicial de la página
st.set_page_config(
    page_title="Análisis Futbolístico",
    page_icon="⚽",
    layout="wide"
)

# Cargar datos
@st.cache_data
def get_data():
    return DataLoader.load_data()

# Cargar y preparar datos
laliga_data, bundesliga_data = get_data()

# Sidebar con menú principal
st.sidebar.title("Menú Principal")
menu_principal = st.sidebar.radio(
    "Seleccione una sección:",
    ["Introducción", "Objetivos", "Metodología", "Herramientas", "Resultados", "Conclusiones", "Comparación Ligas"]
)

if menu_principal == "Introducción":
    st.title("Introducción")
    st.write("""
    La industria del fútbol ha evolucionado significativamente en las principales ligas europeas,
    convirtiéndose en un mercado donde el valor de los jugadores es un indicador crucial de su 
    desempeño y potencial. Este análisis compara las dos principales ligas: LaLiga y Bundesliga.
    """)
    
    lottie_url = "https://lottie.host/embed/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        st_lottie(lottie_coding, height=200, width=300)
    
    # Mostrar tablas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("LaLiga - Datos de Jugadores")
        laliga_display = laliga_data.copy()
        laliga_display["Valor de Mercado en 01/01/2024"] = laliga_display["Valor de Mercado en 01/01/2024"].apply(format_currency)
        laliga_display["Valor de Mercado Actual"] = laliga_display["Valor de Mercado Actual"].apply(format_currency)
        st.markdown(convertir_urls_a_imagenes(laliga_display).to_html(escape=False), unsafe_allow_html=True)
    
    with col2:
        st.subheader("Bundesliga - Datos de Jugadores")
        bundesliga_display = bundesliga_data.copy()
        bundesliga_display["Valor de mercado 01/11/2024"] = bundesliga_display["Valor de mercado 01/11/2024"].apply(format_currency)
        bundesliga_display["Valor de mercado actual"] = bundesliga_display["Valor de mercado actual"].apply(format_currency)
        st.markdown(convertir_urls_a_imagenes(bundesliga_display).to_html(escape=False), unsafe_allow_html=True)

elif menu_principal == "Metodología":
    st.title("Metodología")
    
    # Selección de liga
    liga_seleccionada = st.selectbox("Seleccione la liga:", ["LaLiga", "Bundesliga"])
    
    data = laliga_data if liga_seleccionada == "LaLiga" else bundesliga_data
    valor_inicial_col = "Valor de Mercado en 01/01/2024" if liga_seleccionada == "LaLiga" else "Valor de mercado 01/11/2024"
    valor_actual_col = "Valor de Mercado Actual" if liga_seleccionada == "LaLiga" else "Valor de mercado actual"
    
    visualizacion = st.selectbox(
        "Seleccione tipo de visualización:",
        ["Evolución Individual", "Comparación entre Jugadores", "Tendencias Generales"]
    )
    
    if visualizacion == "Evolución Individual":
        st.subheader(f"Evolución Individual del Valor de Mercado - {liga_seleccionada}")
        nombre_jugador = st.selectbox("Selecciona un jugador:", data['Nombre'].unique())
        
        jugador = data[data['Nombre'] == nombre_jugador]
        if not jugador.empty:
            valor_inicial = jugador[valor_inicial_col].iloc[0]
            valor_final = jugador[valor_actual_col].iloc[0]
            
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
            
            df_mensual = pd.DataFrame({
                'Mes': meses,
                'Valor de Mercado (€)': [format_currency(v) for v in valores]
            })
            st.write("Valores mensuales:")
            st.dataframe(df_mensual)
            
    elif visualizacion == "Comparación entre Jugadores":
        st.subheader(f"Comparación entre Jugadores - {liga_seleccionada}")
        col1, col2 = st.columns(2)
        with col1:
            jugador1 = st.selectbox("Primer jugador:", data['Nombre'].unique())
        with col2:
            jugador2 = st.selectbox("Segundo jugador:", data['Nombre'].unique())
        
        if jugador1 and jugador2:
            fig = go.Figure()
            
            for jugador in [jugador1, jugador2]:
                datos_jugador = data[data['Nombre'] == jugador]
                valor_inicial = datos_jugador[valor_inicial_col].iloc[0]
                valor_final = datos_jugador[valor_actual_col].iloc[0]
                
                meses, valores = generar_valores_mensuales(valor_inicial, valor_final)
                
                fig.add_trace(go.Scatter(
                    x=meses,
                    y=valores,
                    mode='lines+markers',
                    name=jugador,
                    line=dict(width=3),
                    marker=dict(size=10)
                ))
            
            fig.update_layout(
                title='Comparación de Evolución Mensual del Valor de Mercado',
                xaxis_title='Mes',
                yaxis_title='Valor de Mercado (€)',
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig)

elif menu_principal == "Comparación Ligas":
    st.title("Comparación entre LaLiga y Bundesliga")
    
    # Calcular promedios por liga
    laliga_avg = {
        'inicial': laliga_data["Valor de Mercado en 01/01/2024"].mean(),
        'actual': laliga_data["Valor de Mercado Actual"].mean()
    }
    
    bundesliga_avg = {
        'inicial': bundesliga_data["Valor de mercado 01/11/2024"].mean(),
        'actual': bundesliga_data["Valor de mercado actual"].mean()
    }
    
    # Crear gráfico de comparación
    fig = go.Figure()
    
    # Añadir barras para LaLiga
    fig.add_trace(go.Bar(
        name='LaLiga Inicial',
        x=['LaLiga'],
        y=[laliga_avg['inicial']],
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        name='LaLiga Actual',
        x=['LaLiga'],
        y=[laliga_avg['actual']],
        marker_color='lightblue'
    ))
    
    # Añadir barras para Bundesliga
    fig.add_trace(go.Bar(
        name='Bundesliga Inicial',
        x=['Bundesliga'],
        y=[bundesliga_avg['inicial']],
        marker_color='red'
    ))
    
    fig.add_trace(go.Bar(
        name='Bundesliga Actual',
        x=['Bundesliga'],
        y=[bundesliga_avg['actual']],
        marker_color='lightcoral'
    ))
    
    fig.update_layout(
        title='Comparación de Valores Promedio entre LaLiga y Bundesliga',
        yaxis_title='Valor de Mercado Promedio (€)',
        barmode='group'
    )
    
    st.plotly_chart(fig)
    
    # Mostrar estadísticas comparativas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estadísticas LaLiga")
        st.write(laliga_data[["Valor de Mercado en 01/01/2024", "Valor de Mercado Actual"]].describe())
    
    with col2:
        st.subheader("Estadísticas Bundesliga")
        st.write(bundesliga_data[["Valor de mercado 01/11/2024", "Valor de mercado actual"]].describe())

elif menu_principal == "Objetivos":
    st.title("Objetivos del Proyecto")
    st.write("""
    ### Objetivos Principales:
    - Analizar y visualizar el valor de mercado de los jugadores en LaLiga y Bundesliga
    - Evaluar el incremento porcentual del valor de mercado a lo largo del tiempo
    - Identificar patrones y tendencias en la valoración de jugadores
    - Comparar las tendencias entre las dos ligas principales
    """)

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
        - Google Colab
        - Jupiter Notebook
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
    
    liga_seleccionada = st.selectbox("Seleccione la liga:", ["LaLiga", "Bundesliga"])
    data = laliga_data if liga_seleccionada == "LaLiga" else bundesliga_data
    valor_inicial_col = "Valor de Mercado en 01/01/2024" if liga_seleccionada == "LaLiga" else "Valor de mercado 01/11/2024"
    valor_actual_col = "Valor de Mercado Actual" if liga_seleccionada == "LaLiga" else "Valor de mercado actual"
    
    tab1, tab2, tab3 = st.tabs(["Estadísticas Generales", "Análisis de Tendencias", "Recomendaciones"])
    
    with tab1:
        st.header(f"Estadísticas Generales - {liga_seleccionada}")
        st.write("Estadísticas descriptivas de los valores de mercado:")
        st.dataframe(data[[valor_inicial_col, valor_actual_col]].describe())
        
    with tab2:
        st.header(f"Análisis de Tendencias - {liga_seleccionada}")
        fig = go.Figure()
        fig.add_trace(go.Box(
            y=data[valor_inicial_col],
            name='Valor Inicial'
        ))
        fig.add_trace(go.Box(
            y=data[valor_actual_col],
            name='Valor Actual'
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
        - Comparativa entre ligas
        """)

else:  # Conclusiones
    st.title("Conclusiones")
    st.write("""
    ### Principales Hallazgos:
    - El análisis de datos en el fútbol ofrece insights valiosos para la toma de decisiones
    - Las tendencias del mercado muestran patrones significativos en la valoración de jugadores
    - La gestión basada en datos puede mejorar significativamente las estrategias de los equipos
    - La comparación entre ligas permite identificar diferencias en las valoraciones de mercado
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("ANÁLISIS DE LAS ESTADÍSTICAS QUE TIENEN MAYOR CORRELACIÓN CON EL VALOR DE MERCADO DE LOS JUGADORES DE FUTBOL EN ESPAÑA Y ALEMANIA")
