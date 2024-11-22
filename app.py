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
    bundesliga_data = pd.read_csv('https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/main/valores_mercado_bundesliga_actualizado_v2.csv')
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



elif menu_principal == "Metodología":
    st.title("Metodología")
    
    # Comprobar si la opción seleccionada es "Comparativa"
    if liga_seleccionada == "Comparativa":
        st.subheader("Comparativa de Valor de Mercado: LaLiga vs Bundesliga")
        
        # Preparar los datos para la gráfica comparativa
        fig = go.Figure()
        
        # Añadir los datos de LaLiga
        fig.add_trace(go.Box(
            y=spain_data['Valor de Mercado Actual'],
            name='LaLiga',
            boxmean='sd',  # Mostrar la media y las desviaciones
            marker=dict(color='blue')
        ))

        # Añadir los datos de Bundesliga
        fig.add_trace(go.Box(
            y=bundesliga_data['Valor de Mercado Actual'],
            name='Bundesliga',
            boxmean='sd',  # Mostrar la media y las desviaciones
            marker=dict(color='green')
        ))

        # Actualizar el diseño de la gráfica
        fig.update_layout(
            title="Distribución de Valores de Mercado por Liga",
            yaxis_title="Valor de Mercado (€)",
            showlegend=False
        )
        
        # Mostrar la gráfica comparativa
        st.plotly_chart(fig)
        
        # Añadir el análisis escrito debajo de la gráfica
        st.write("""
        ### Análisis Comparativo:
        Al comparar los valores de mercado actuales entre **LaLiga** y **Bundesliga**, 
        se observan diferencias clave en la distribución de los valores. 
        La **LaLiga** presenta una mayor concentración de jugadores de alto valor, 
        mientras que en **Bundesliga** los valores tienden a estar más dispersos.
        
        Estas diferencias podrían estar relacionadas con factores como:
        - **Tamaño de los equipos** y su capacidad económica.
        - **Desarrollo de jugadores** y su potencial de crecimiento.
        - **Intereses de los inversores** y su influencia en la valoración de jugadores.
        
        Esta comparativa puede ayudar a identificar tendencias de inversión y áreas 
        de oportunidad dentro de los mercados de ambas ligas.
        """)
    
    else:
        # Para las otras visualizaciones (Evolución Individual, Comparación entre Jugadores, etc.)
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
                if liga_seleccionada == "LaLiga":
                    valor_inicial = jugador['Valor de Mercado en 01/01/2024'].iloc[0]
                    valor_final = jugador['Valor de Mercado Actual'].iloc[0]
                else:
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
                
                df_mensual = pd.DataFrame({
                    'Mes': meses,
                    'Valor de Mercado (€)': [f"€{int(v):,}" for v in valores]
                })
                st.write("Valores mensuales:")
                st.dataframe(df_mensual)

elif menu_principal == "Objetivos":
    st.title("Objetivos del Proyecto")
    st.write("""
    ### Objetivos Principales:
    - Analizar y visualizar el valor de mercado de los jugadores en LaLiga y Bundesliga
    - Evaluar el incremento porcentual del valor de mercado a lo largo del tiempo
    - Identificar patrones y tendencias en la valoración de jugadores
    - Comparar las valoraciones entre las diferentes ligas
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
    
    if liga_seleccionada == "Comparativa":
        tab1, tab2, tab3 = st.tabs(["Estadísticas Generales", "Análisis Comparativo", "Recomendaciones"])
        
        with tab1:
            st.header("Estadísticas Generales")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("LaLiga")
                st.dataframe(spain_data[['Valor de Mercado en 01/01/2024', 'Valor de Mercado Actual']].describe())
            
            with col2:
                st.subheader("Bundesliga")
                st.dataframe(bundesliga_data[['Valor de Mercado en 01/01/2024', 'Valor de Mercado Actual']].describe())
        
        with tab2:
            st.header("Análisis Comparativo")
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=spain_data['Valor de Mercado Actual'],
                name='LaLiga'
            ))
            
            fig.add_trace(go.Box(
                y=bundesliga_data['Valor de Mercado Actual'],
                name='Bundesliga'
            ))
            
            fig.update_layout(
                title='Distribución de Valores de Mercado por Liga',
                yaxis_title='Valor de Mercado (€)'
            )
            st.plotly_chart(fig)
        
        with tab3:
            st.header("Recomendaciones")
            st.write("""
            Basadas en el análisis comparativo:
            - Recomendaciones para clubes de ambas ligas
            - Estrategias de inversión considerando diferencias entre mercados
            - Oportunidades de mercado en ambas ligas
            """)
    else:
        tab1, tab2, tab3 = st.tabs(["Estadísticas Generales", "Análisis de Tendencias", "Recomendaciones"])
        
        with tab1:
            st.header("Estadísticas Generales")
            if liga_seleccionada == "LaLiga":
                st.dataframe(spain_data[['Valor de Mercado en 01/01/2024', 'Valor de Mercado Actual']].describe())
            else:
                st.dataframe(bundesliga_data[['Valor de Mercado en 01/01/2024', 'Valor de Mercado Actual']].describe())
        
        with tab2:
            st.header("Análisis de Tendencias")
            fig = go.Figure()
            
            if liga_seleccionada == "LaLiga":
                fig.add_trace(go.Box(
                    y=spain_data['Valor de Mercado en 01/01/2024'],
                    name='Enero 2024'
                ))
                fig.add_trace(go.Box(
                    y=spain_data['Valor de Mercado Actual'],
                    name='Actual'
                ))
            else:
                fig.add_trace(go.Box(
                    y=bundesliga_data['Valor de Mercado en 01/01/2024'],
                    name='Enero 2024'
                ))
                fig.add_trace(go.Box(
                    y=bundesliga_data['Valor de Mercado Actual'],
                    name='Actual'
                ))
            
            fig.update_layout(
                title=f'Distribución de Valores de Mercado - {liga_seleccionada}',
                yaxis_title='Valor de Mercado (€)'
            )
            st.plotly_chart(fig)
        
        with tab3:
            st.header("Recomendaciones")
            st.write(f"""
            Basadas en el análisis de datos de {liga_seleccionada}:
            - Recomendaciones para clubes
            - Estrategias de inversión
            - Oportunidades de mercado
            """)

else:  # Conclusiones
    st.title("Conclusiones")
    if liga_seleccionada == "Comparativa":
        st.write("""
        ### Principales Hallazgos:
        - Comparativa entre LaLiga y Bundesliga muestra patrones interesantes en la valoración de jugadores
        - Las diferencias entre mercados ofrecen oportunidades únicas de inversión
        - La gestión basada en datos puede mejorar significativamente las estrategias de los equipos en ambas ligas
        """)
    else:
        st.write(f"""
        ### Principales Hallazgos en {liga_seleccionada}:
        - El análisis de datos en el fútbol ofrece insights valiosos para la toma de decisiones
        - Las tendencias del mercado muestran patrones significativos en la valoración de jugadores
        - La gestión basada en datos puede mejorar significativamente las estrategias de los equipos
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("ANÁLISIS DE LAS ESTADÍSTICAS QUE TIENEN MAYOR CORRELACIÓN CON EL VALOR DE MERCADO DE LOS JUGADORES DE FUTBOL EN ESPAÑA Y ALEMANIA")


