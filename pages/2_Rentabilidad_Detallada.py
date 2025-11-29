import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Rentabilidad Detallada", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
df = data.get('merged_ventas')

st.title("Rentabilidad Detallada")

if df is not None:
    # Filters
    st.sidebar.header("Filtros")
    years = df['fecha'].dt.year.unique()
    selected_year = st.sidebar.selectbox("Seleccionar Año", sorted(years, reverse=True))
    df_filtered = df[df['fecha'].dt.year == selected_year]

    # 1. Matrix: Profitability by Category & Region
    st.subheader("Rentabilidad (Margen %) por Categoría y Región")
    if 'categoria' in df_filtered.columns and 'region' in df_filtered.columns:
        pivot_table = df_filtered.pivot_table(
            values='margen_pct', 
            index='categoria', 
            columns='region', 
            aggfunc='mean'
        )
        st.dataframe(pivot_table.style.format("{:.2f}%").background_gradient(cmap="RdYlGn"))
    else:
        st.info("Columnas de Categoría o Región no encontradas.")

    col1, col2 = st.columns(2)

    # 2. Margin by Channel (Sale Type)
    with col1:
        st.subheader("Margen Bruto por Esquema de Venta")
        if 'tipo_venta' in df_filtered.columns:
            # Simplify 'tipo_venta' to 'Contado' vs 'Crédito' if needed, or use as is
            # Assuming 'tipo_venta' contains values like 'Contado', 'Crédito 30 días', etc.
            df_filtered['canal_simplificado'] = df_filtered['tipo_venta'].apply(lambda x: 'Contado' if 'Contado' in str(x) else 'Crédito')
            
            fig_channel = px.bar(
                df_filtered.groupby('canal_simplificado')['margen_total_cop'].sum().reset_index(), 
                x='canal_simplificado', 
                y='margen_total_cop',
                title="Margen por Canal (Contado vs Crédito)"
            )
            st.plotly_chart(fig_channel, use_container_width=True)

    # 3. Pareto of Portfolios
    with col2:
        st.subheader("Pareto de Rentabilidad (Categorías)")
        if 'categoria' in df_filtered.columns:
            pareto_df = df_filtered.groupby('categoria')['margen_total_cop'].sum().reset_index()
            pareto_df = pareto_df.sort_values('margen_total_cop', ascending=False)
            pareto_df['cumulative_margin'] = pareto_df['margen_total_cop'].cumsum()
            pareto_df['cumulative_pct'] = pareto_df['cumulative_margin'] / pareto_df['margen_total_cop'].sum()
            
            # Identify top 80%
            pareto_df['top_80'] = pareto_df['cumulative_pct'] <= 0.80
            
            fig_pareto = px.bar(
                pareto_df, 
                x='categoria', 
                y='margen_total_cop', 
                color='top_80',
                title="Pareto de Margen por Categoría (80/20)"
            )
            st.plotly_chart(fig_pareto, use_container_width=True)
else:
    st.error("No hay datos de ventas disponibles.")
