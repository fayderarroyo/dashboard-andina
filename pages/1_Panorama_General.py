import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Panorama General", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
df = data.get('merged_ventas')

st.title("Panorama General de Ventas y Margen")

# Filters
st.sidebar.header("Filtros")
if df is not None:
    years = sorted(df['fecha'].dt.year.unique(), reverse=True)
    options = ["Todos"] + list(years)
    selected_year = st.sidebar.selectbox("Seleccionar Año", options)
    
    if selected_year == "Todos":
        df_filtered = df.copy()
        title_suffix = " (Todos los Años)"
    else:
        df_filtered = df[df['fecha'].dt.year == selected_year]
        title_suffix = f" ({selected_year})"
    
    # KPIs
    total_ventas = df_filtered['subtotal_cop'].sum()
    total_margen = df_filtered['margen_total_cop'].sum()
    margen_pct = (total_margen / total_ventas) * 100 if total_ventas > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
    col2.metric("Margen Bruto", f"${total_margen:,.0f}")
    col3.metric("Margen %", f"{margen_pct:.2f}%")
    
    # Charts
    st.subheader(f"Tendencia de Ventas y Margen{title_suffix}")
    
    if selected_year == "Todos":
        # Multi-line chart: X=Month, Y=Value, Color=Year
        df_filtered['año'] = df_filtered['fecha'].dt.year
        df_filtered['mes'] = df_filtered['fecha'].dt.month_name(locale='es_ES') # Requires locale or just month number
        # Fallback for locale if not set or windows specific issues, let's use month number or custom map
        month_map = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
                     7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
        df_filtered['mes_num'] = df_filtered['fecha'].dt.month
        df_filtered['mes_nombre'] = df_filtered['mes_num'].map(month_map)
        
        df_monthly = df_filtered.groupby(['año', 'mes_num', 'mes_nombre']).agg({
            'subtotal_cop': 'sum',
            'margen_total_cop': 'sum'
        }).reset_index()
        
        df_monthly.sort_values(['año', 'mes_num'], inplace=True)
        
        fig_sales = px.line(df_monthly, x='mes_nombre', y='subtotal_cop', color='año', 
                            title='Comparativo de Ventas Mensuales por Año', markers=True,
                            category_orders={'mes_nombre': list(month_map.values())})
        st.plotly_chart(fig_sales, use_container_width=True)
        
        fig_margin = px.line(df_monthly, x='mes_nombre', y='margen_total_cop', color='año', 
                             title='Comparativo de Margen Bruto Mensual por Año', markers=True,
                             category_orders={'mes_nombre': list(month_map.values())})
        st.plotly_chart(fig_margin, use_container_width=True)
        
    else:
        # Single year chart (Original logic)
        df_monthly = df_filtered.groupby(df_filtered['fecha'].dt.to_period('M')).agg({
            'subtotal_cop': 'sum',
            'margen_total_cop': 'sum'
        }).reset_index()
        df_monthly['fecha'] = df_monthly['fecha'].dt.to_timestamp()
        
        fig_sales = px.line(df_monthly, x='fecha', y='subtotal_cop', title='Ventas Mensuales', markers=True)
        st.plotly_chart(fig_sales, use_container_width=True)
        
        fig_margin = px.line(df_monthly, x='fecha', y='margen_total_cop', title='Margen Bruto Mensual', markers=True)
        st.plotly_chart(fig_margin, use_container_width=True)
else:
    st.error("No hay datos de ventas disponibles.")
