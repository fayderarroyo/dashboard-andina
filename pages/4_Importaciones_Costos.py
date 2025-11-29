import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Importaciones y Costos", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
imports = data.get('importaciones')

st.title("Importaciones, TRM y Costos")

if imports is not None:
    # KPI
    total_imports_usd = imports['costo_mercancia_usd'].sum()
    st.metric("Total Compras en USD", f"${total_imports_usd:,.2f}")
    
    col1, col2 = st.columns(2)
    
    # 1. TRM Trend
    with col1:
        st.subheader("Evolución de la TRM")
        if 'trm' in imports.columns and 'fecha_orden' in imports.columns:
            imports['fecha_orden'] = pd.to_datetime(imports['fecha_orden'])
            imports_sorted = imports.sort_values('fecha_orden')
            
            fig_trm = px.line(imports_sorted, x='fecha_orden', y='trm', title="Tendencia Histórica de la TRM")
            st.plotly_chart(fig_trm, use_container_width=True)
        else:
            st.info("Datos de TRM o Fecha no disponibles.")
            
    # 2. Imports by Country
    with col2:
        st.subheader("Distribución de Importaciones por País")
        if 'pais_origen' in imports.columns:
            country_dist = imports.groupby('pais_origen')['costo_mercancia_usd'].sum().reset_index()
            
            fig_country = px.pie(
                country_dist, 
                values='costo_mercancia_usd', 
                names='pais_origen', 
                title="Importaciones por País (USD)"
            )
            st.plotly_chart(fig_country, use_container_width=True)
            
    st.dataframe(imports)

else:
    st.error("No hay datos de importaciones disponibles.")
