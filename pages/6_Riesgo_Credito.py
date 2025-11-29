import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Riesgo de Crédito", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
cartera = data.get('cartera')
clientes = data.get('clientes')

st.title("Cartera, Mora y Riesgo de Crédito")

if cartera is not None:
    # Merge with client names if needed
    if clientes is not None:
        cartera['cliente_id'] = cartera['cliente_id'].astype(str)
        clientes['cliente_id'] = clientes['cliente_id'].astype(str)
        # Avoid duplicate columns if already merged in data_loader (it wasn't for cartera)
        cartera = cartera.merge(clientes[['cliente_id', 'nombre_cliente']], on='cliente_id', how='left')

    # KPIs
    total_cartera = cartera['saldo_cop'].sum()
    mora_cartera = cartera[cartera['dias_mora'] > 0]['saldo_cop'].sum()
    pct_mora = (mora_cartera / total_cartera) * 100 if total_cartera > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Cartera Total", f"${total_cartera:,.0f}")
    col2.metric("Monto en Mora", f"${mora_cartera:,.0f}")
    col3.metric("% Cartera en Mora", f"{pct_mora:.2f}%")
    
    # 1. Aging Portfolio (Antigüedad)
    st.subheader("Antigüedad de la Cartera en Mora")
    
    def classify_aging(days):
        if days <= 0:
            return 'Al día'
        elif days <= 30:
            return '1-30 días'
        elif days <= 60:
            return '31-60 días'
        elif days <= 90:
            return '61-90 días'
        else:
            return '> 90 días'
            
    cartera['rango_mora'] = cartera['dias_mora'].apply(classify_aging)
    
    aging_dist = cartera[cartera['dias_mora'] > 0].groupby('rango_mora')['saldo_cop'].sum().reset_index()
    
    # Order the categories
    order = ['1-30 días', '31-60 días', '61-90 días', '> 90 días']
    
    fig_aging = px.bar(
        aging_dist, 
        x='rango_mora', 
        y='saldo_cop', 
        category_orders={'rango_mora': order},
        title="Distribución de Cartera Vencida por Edades",
        color='rango_mora'
    )
    st.plotly_chart(fig_aging, use_container_width=True)
    
    col_risk1, col_risk2 = st.columns(2)
    
    # 2. Risk by Client (Top 5 Mora)
    with col_risk1:
        st.subheader("Top 5 Clientes en Mora")
        top_mora = cartera[cartera['dias_mora'] > 0].groupby('nombre_cliente')['saldo_cop'].sum().reset_index()
        top_mora = top_mora.sort_values('saldo_cop', ascending=False).head(5)
        
        fig_top_mora = px.bar(
            top_mora,
            x='saldo_cop',
            y='nombre_cliente',
            orientation='h',
            title="Top 5 Clientes con Mayor Mora"
        )
        st.plotly_chart(fig_top_mora, use_container_width=True)
        
    # 3. Provision (Hypothetical calculation based on aging)
    with col_risk2:
        st.subheader("Provisión Estimada de Cartera")
        # Simple provision policy example:
        # > 90 days: 100%
        # 61-90 days: 50%
        # 31-60 days: 20%
        # 1-30 days: 5%
        
        def calc_provision(row):
            days = row['dias_mora']
            saldo = row['saldo_cop']
            if days > 90: return saldo * 1.0
            elif days > 60: return saldo * 0.5
            elif days > 30: return saldo * 0.2
            elif days > 0: return saldo * 0.05
            return 0
            
        cartera['provision'] = cartera.apply(calc_provision, axis=1)
        total_provision = cartera['provision'].sum()
        
        st.metric("Provisión Total Estimada", f"${total_provision:,.0f}")
        st.write("Nota: Cálculo basado en política estándar (>90: 100%, 61-90: 50%, etc.)")

else:
    st.error("No hay datos de cartera disponibles.")
