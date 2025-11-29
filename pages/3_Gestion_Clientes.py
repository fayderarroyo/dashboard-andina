import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Gestión de Clientes", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
df = data.get('merged_ventas')
cartera = data.get('cartera')

st.title("Gestión de Clientes: Valor, Concentración y Riesgo")

if df is not None:
    # Filters
    st.sidebar.header("Filtros")
    years = df['fecha'].dt.year.unique()
    selected_year = st.sidebar.selectbox("Seleccionar Año", sorted(years, reverse=True))
    df_filtered = df[df['fecha'].dt.year == selected_year]

    col1, col2 = st.columns(2)

    # 1. Top 10 Clients
    with col1:
        st.subheader("Top 10 Clientes (Ventas)")
        top_clients = df_filtered.groupby('nombre_cliente')['subtotal_cop'].sum().reset_index()
        top_clients = top_clients.sort_values('subtotal_cop', ascending=False).head(10)
        st.dataframe(top_clients.style.format({"subtotal_cop": "${:,.0f}"}))

    # 2. Concentration Analysis
    with col2:
        st.subheader("Concentración de Ventas (Top 10)")
        total_sales = df_filtered['subtotal_cop'].sum()
        top_10_sales = top_clients['subtotal_cop'].sum()
        concentration_pct = (top_10_sales / total_sales) * 100
        
        st.metric("Concentración Top 10 Clientes", f"{concentration_pct:.2f}%")
        
        fig_pie = px.pie(values=[top_10_sales, total_sales - top_10_sales], names=['Top 10', 'Otros'], title="Distribución de Ventas")
        st.plotly_chart(fig_pie, use_container_width=True)

    # 3. Customer Segmentation
    st.subheader("Segmentación de Clientes por Valor")
    client_value = df_filtered.groupby('nombre_cliente')['subtotal_cop'].sum().reset_index()
    
    # Simple segmentation logic
    def segment_client(value):
        if value > client_value['subtotal_cop'].quantile(0.8):
            return 'Alto Valor'
        elif value > client_value['subtotal_cop'].quantile(0.5):
            return 'Valor Medio'
        else:
            return 'Bajo Valor'
            
    client_value['segmento_valor'] = client_value['subtotal_cop'].apply(segment_client)
    
    fig_segment = px.bar(
        client_value['segmento_valor'].value_counts().reset_index(), 
        x='segmento_valor', 
        y='count',
        title="Distribución de Clientes por Segmento de Valor"
    )
    st.plotly_chart(fig_segment, use_container_width=True)

    # 4. Link to Risk
    st.subheader("Resumen de Riesgo de Crédito")
    if cartera is not None:
        total_cartera = cartera['saldo_cop'].sum()
        mora_cartera = cartera[cartera['dias_mora'] > 0]['saldo_cop'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Cartera Total Pendiente", f"${total_cartera:,.0f}")
        c2.metric("Cartera en Mora", f"${mora_cartera:,.0f}")
        
        st.info("Para un análisis detallado de la cartera, vaya a la página 'Riesgo de Crédito'.")

else:
    st.error("No hay datos de ventas disponibles.")
