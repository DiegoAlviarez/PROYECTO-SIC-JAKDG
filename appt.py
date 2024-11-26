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
    spain_data = pd.read_csv('https://raw.githubusercontent.com/AndersonP444/PROYECTO-SIC-JAKDG/blob/main/CSV%20DESPUES%20DEL%20PROCESAMIENTO%20DE%20DATOS/valores_mercado_actualizados_con_estadisticas.csv')
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

if menu_principal == "Introducción":
    st.title("Introducción")
    st.write("""
    La industria del fútbol ha evolucionado significativamente, convirtiéndose en un mercado 
    donde el valor de los jugadores es un indicador crucial de su desempeño y potencial.
    """)

    # Cargar animación Lottie
    lottie_url = "https://lottie.host/embed/3d48d4b9-51ad-4b7d-9d28-5e248cace11/Rz3QtSCq3.json"
    lottie_coding = load_lottieurl(lottie_url)
    if lottie_coding:
        st_lottie(lottie_coding, height=200, width=300)

    # Mostrar datos según la liga seleccionada
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
            tabla_laliga_html = convertir_urls_a_imagenes(spain_data)
            st.markdown(tabla_laliga_html.to_html(escape=False), unsafe_allow_html=True)
        
        with col2:
            st.write("### Bundesliga")
            tabla_bundesliga_html = convertir_urls_a_imagenes(bundesliga_data)
            st.markdown(tabla_bundesliga_html.to_html(escape=False), unsafe_allow_html=True)

    # Mostrar tabla individual si no es Comparativa
    if liga_seleccionada != "Comparativa":
        with st.container():
            st.subheader(title)
            data_con_imagenes = convertir_urls_a_imagenes(data_to_show)
            st.markdown(data_con_imagenes.to_html(escape=False), unsafe_allow_html=True)

elif menu_principal == "Objetivos":
    st.title("Objetivos del Proyecto")
    st.write("""
    ### Objetivos Principales:
    - Analizar y visualizar el valor de mercado de los jugadores en LaLiga y Bundesliga
    - Evaluar el incremento porcentual del valor de mercado a lo largo del tiempo
    - Identificar patrones y tendencias en la valoración de jugadores
    - Comparar las valoraciones entre las diferentes ligas
    """)

elif menu_principal == "Metodología":
    st.title("Metodología")
    
    if liga_seleccionada == "Comparativa":
        st.subheader("Comparativa de Valor de Mercado: LaLiga vs Bundesliga")

        # 1. Player Selection Comparison
        col1, col2 = st.columns(2)
        with col1:
            jugadores_laliga = st.multiselect(
                "Selecciona jugadores de LaLiga:",
                spain_data['Nombre'].unique(),
                max_selections=5
            )
        with col2:
            jugadores_bundesliga = st.multiselect(
                "Selecciona jugadores de Bundesliga:",
                bundesliga_data['Nombre'].unique(),
                max_selections=5
            )

        if jugadores_laliga or jugadores_bundesliga:
            # Create scatter plot for selected players
            fig_scatter = go.Figure()

            # Add selected LaLiga players
            if jugadores_laliga:
                laliga_selected = spain_data[spain_data['Nombre'].isin(jugadores_laliga)]
                fig_scatter.add_trace(go.Scatter(
                    x=laliga_selected['Nombre'],
                    y=laliga_selected['Valor de Mercado Actual'],
                    mode='markers+text',
                    name='LaLiga',
                    text=laliga_selected['Nombre'],
                    textposition='top center',
                    marker=dict(
                        size=15,
                        color='blue',
                        opacity=0.6
                    )
                ))

            # Add selected Bundesliga players
            if jugadores_bundesliga:
                bundesliga_selected = bundesliga_data[bundesliga_data['Nombre'].isin(jugadores_bundesliga)]
                fig_scatter.add_trace(go.Scatter(
                    x=bundesliga_selected['Nombre'],
                    y=bundesliga_selected['Valor de Mercado Actual'],
                    mode='markers+text',
                    name='Bundesliga',
                    text=bundesliga_selected['Nombre'],
                    textposition='top center',
                    marker=dict(
                        size=15,
                        color='red',
                        opacity=0.6
                    )
                ))

            # Update layout
            fig_scatter.update_layout(
                title='Comparación de Valores de Mercado de Jugadores Seleccionados',
                xaxis_title='Jugadores',
                yaxis_title='Valor de Mercado (€)',
                showlegend=True,
                height=600,
                xaxis={'showticklabels': False}
            )

            # Show the scatter plot
            st.plotly_chart(fig_scatter)

            # Add analysis text for selected players
            if jugadores_laliga and jugadores_bundesliga:
                laliga_avg = laliga_selected['Valor de Mercado Actual'].mean()
                bundesliga_avg = bundesliga_selected['Valor de Mercado Actual'].mean()
                
                st.write("""
                ### Análisis de la Comparación de Jugadores Seleccionados:
                
                La gráfica muestra la comparación de valores de mercado entre los jugadores seleccionados:
                """)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"""
                    **LaLiga (Azul)**:
                    - Valor promedio: €{int(laliga_avg):,}
                    - Jugadores seleccionados: {len(jugadores_laliga)}
                    """)
                
                with col2:
                    st.write(f"""
                    **Bundesliga (Rojo)**:
                    - Valor promedio: €{int(bundesliga_avg):,}
                    - Jugadores seleccionados: {len(jugadores_bundesliga)}
                    """)

        # 2. General Distribution Comparison (Violin Plot)
        st.subheader("Distribución General de Valores de Mercado")
        
        fig_violin = go.Figure()

        # Add LaLiga data
        fig_violin.add_trace(go.Violin(
            y=spain_data['Valor de Mercado Actual'],
            name='LaLiga',
            box_visible=True,
            meanline_visible=True,
            line_color='blue',
            fillcolor='rgba(0, 0, 255, 0.3)',
            opacity=0.7
        ))

        # Add Bundesliga data
        fig_violin.add_trace(go.Violin(
            y=bundesliga_data['Valor de Mercado Actual'],
            name='Bundesliga',
            box_visible=True,
            meanline_visible=True,
            line_color='red',
            fillcolor='rgba(255, 0, 0, 0.3)',
            opacity=0.7
        ))

        fig_violin.update_layout(
            title="Distribución de Valores de Mercado por Liga",
            yaxis_title="Valor de Mercado (€)",
            xaxis_title="Ligas",
            violingap=0.5,
            violingroupgap=0.3,
            showlegend=True
        )

        st.plotly_chart(fig_violin)

        st.write("""
        ### Análisis de la Distribución General:
        
        El gráfico de violín muestra la distribución completa de los valores de mercado en ambas ligas:
        
        - **Forma de la distribución**: Indica la concentración de jugadores en diferentes rangos de valor
        - **Línea central**: Representa la mediana del valor de mercado
        - **Ancho**: Muestra la densidad de jugadores en cada nivel de valor
        """)

        # 3. Box Plot Comparison
        st.subheader("Comparativa Estadística")
        
        fig_box = go.Figure()
        
        fig_box.add_trace(go.Box(
            y=spain_data['Valor de Mercado Actual'],
            name='LaLiga',
            boxpoints='outliers',
            marker_color='blue',
            line_color='blue'
        ))
        
        fig_box.add_trace(go.Box(
            y=bundesliga_data['Valor de Mercado Actual'],
            name='Bundesliga',
            boxpoints='outliers',
            marker_color='red',
            line_color='red'
        ))
        
        fig_box.update_layout(
            title='Análisis Estadístico de Valores de Mercado',
            yaxis_title='Valor de Mercado (€)',
            showlegend=True
        )
        
        st.plotly_chart(fig_box)

        # Statistical Analysis
        laliga_stats = spain_data['Valor de Mercado Actual'].describe()
        bundesliga_stats = bundesliga_data['Valor de Mercado Actual'].describe()

        st.write("""
        ### Análisis Estadístico Comparativo:
        """)

        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**LaLiga:**")
            st.write(f"""
            - Mediana: €{int(laliga_stats['50%']):,}
            - Promedio: €{int(laliga_stats['mean']):,}
            - Valor Máximo: €{int(laliga_stats['max']):,}
            - Valor Mínimo: €{int(laliga_stats['min']):,}
            """)
        
        with col2:
            st.write("**Bundesliga:**")
            st.write(f"""
            - Mediana: €{int(bundesliga_stats['50%']):,}
            - Promedio: €{int(bundesliga_stats['mean']):,}
            - Valor Máximo: €{int(bundesliga_stats['max']):,}
            - Valor Mínimo: €{int(bundesliga_stats['min']):,}
            """)

    else:
        # Individual League Analysis
        st.subheader(f"Análisis de {liga_seleccionada}")
        
        # Select data based on league
        data = spain_data if liga_seleccionada == "LaLiga" else bundesliga_data
        
        # 1. Top Players by Market Value
        st.subheader("Top 10 Jugadores por Valor de Mercado")
        
        top_10 = data.nlargest(10, 'Valor de Mercado Actual')
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=top_10['Nombre'],
            y=top_10['Valor de Mercado Actual'],
            marker_color='blue' if liga_seleccionada == "LaLiga" else 'red'
        ))
        
        fig_bar.update_layout(
            title=f'Top 10 Jugadores por Valor de Mercado - {liga_seleccionada}',
            xaxis_title='Jugadores',
            yaxis_title='Valor de Mercado (€)',
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig_bar)

        # 2. Value Distribution
        st.subheader("Distribución de Valores de Mercado")
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=data['Valor de Mercado Actual'],
            nbinsx=30,
            marker_color='blue' if liga_seleccionada == "LaLiga" else 'red'
        ))
        
        fig_hist.update_layout(
            title=f'Distribución de Valores de Mercado - {liga_seleccionada}',
            xaxis_title='Valor de Mercado (€)',
            yaxis_title='Número de Jugadores'
        )
        
        st.plotly_chart(fig_hist)

        # 3. Value Evolution
        st.subheader("Evolución del Valor de Mercado")
        
        # Calculate value changes
        data['Cambio'] = data['Valor de Mercado Actual'] - data['Valor de Mercado en 01/01/2024']
        data['Cambio_Porcentual'] = (data['Cambio'] / data['Valor de Mercado en 01/01/2024']) * 100
        
        top_changes = data.nlargest(5, 'Cambio_Porcentual')
        
        fig_changes = go.Figure()
        fig_changes.add_trace(go.Bar(
            x=top_changes['Nombre'],
            y=top_changes['Cambio_Porcentual'],
            marker_color='blue' if liga_seleccionada == "LaLiga" else 'red'
        ))
        
        fig_changes.update_layout(
            title=f'Top 5 Incrementos de Valor - {liga_seleccionada}',
            xaxis_title='Jugadores',
            yaxis_title='Cambio Porcentual (%)',
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig_changes)

        # Statistical Summary
        st.subheader("Resumen Estadístico")
        
        stats = data['Valor de Mercado Actual'].describe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"""
            **Valores Actuales:**
            - Mediana: €{int(stats['50%']):,}
            - Promedio: €{int(stats['mean']):,}
            - Valor Máximo: €{int(stats['max']):,}
            """)
        
        with col2:
            st.write(f"""
            **Cambios desde Enero 2024:**
            - Cambio Promedio: {data['Cambio_Porcentual'].mean():.2f}%
            - Mayor Incremento: {data['Cambio_Porcentual'].max():.2f}%
            - Menor Incremento: {data['Cambio_Porcentual'].min():.2f}%
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
