import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Inventario y Operación", layout="wide")

if 'data' not in st.session_state:
    st.warning("Por favor vaya a la página principal para cargar los datos.")
    st.stop()

data = st.session_state['data']
inventory = data.get('inventario')
sales = data.get('merged_ventas')
products = data.get('productos')

st.title("Inventario y Operación")

if inventory is not None and not inventory.empty:
    # Ensure date format
    inventory['fecha_corte'] = pd.to_datetime(inventory['fecha_corte'])
    
    # 1. Current Inventory State (Latest Snapshot)
    latest_date = inventory['fecha_corte'].max()
    current_inventory = inventory[inventory['fecha_corte'] == latest_date].copy()
    
    st.write(f"**Fecha de Corte de Inventario:** {latest_date.date()}")
    
    # Merge with products for names if needed (though inventory has category/subcategory)
    if products is not None:
        current_inventory['producto_id'] = current_inventory['producto_id'].astype(str)
        products['producto_id'] = products['producto_id'].astype(str)
        # Avoid duplicate columns
        cols_to_merge = [c for c in products.columns if c not in current_inventory.columns and c != 'producto_id']
        if cols_to_merge:
            current_inventory = current_inventory.merge(products[['producto_id'] + cols_to_merge], on='producto_id', how='left')

    # KPIs
    total_inventory_val = current_inventory['valor_inventario_cop'].sum()
    stock_out_count = current_inventory[current_inventory['stock_unidades'] <= 0].shape[0]
    
    # Overstock: Simple rule, e.g., top 10% value? Or we rely on rotation later.
    # For now, just show value and stockouts.
    
    col1, col2 = st.columns(2)
    col1.metric("Valor Total Inventario (Actual)", f"${total_inventory_val:,.0f}")
    col2.metric("Referencias en Ruptura (Stock 0)", stock_out_count)
    
    # 2. Calculate Rotation (using 2024 data if available, or matching period)
    # Rotation = COGS / Avg Inventory
    
    st.subheader("Análisis de Rotación (Año 2024)")
    
    if sales is not None:
        # Filter Sales for 2024
        sales_2024 = sales[sales['fecha'].dt.year == 2024]
        
        if not sales_2024.empty:
            # Calculate COGS per product
            # COGS = Subtotal - Margen
            sales_2024['cogs'] = sales_2024['subtotal_cop'] - sales_2024['margen_total_cop']
            product_cogs = sales_2024.groupby('producto_id')['cogs'].sum().reset_index()
            product_cogs['producto_id'] = product_cogs['producto_id'].astype(str)
            
            # Calculate Avg Inventory per product for 2024
            inv_2024 = inventory[inventory['fecha_corte'].dt.year == 2024]
            avg_inv = inv_2024.groupby('producto_id')['valor_inventario_cop'].mean().reset_index()
            avg_inv.rename(columns={'valor_inventario_cop': 'avg_inventory_value'}, inplace=True)
            avg_inv['producto_id'] = avg_inv['producto_id'].astype(str)
            
            # Merge
            rotation_df = pd.merge(product_cogs, avg_inv, on='producto_id', how='inner')
            
            # Calculate Rotation
            # Avoid division by zero
            rotation_df = rotation_df[rotation_df['avg_inventory_value'] > 0]
            rotation_df['rotacion_veces'] = rotation_df['cogs'] / rotation_df['avg_inventory_value']
            rotation_df['rotacion_dias'] = 365 / rotation_df['rotacion_veces']
            
            # Merge with product names/categories for visualization
            if products is not None:
                 rotation_df = rotation_df.merge(products[['producto_id', 'descripcion', 'categoria']], on='producto_id', how='left')
            
            # 2.1 Rotation by Category
            avg_rot_cat = rotation_df.groupby('categoria')['rotacion_dias'].mean().reset_index()
            fig_rot = px.bar(avg_rot_cat, x='categoria', y='rotacion_dias', title="Rotación Promedio (Días) por Categoría")
            st.plotly_chart(fig_rot, use_container_width=True)
            
            # 2.2 Danger Chart
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.subheader("Top 10 Mayor Rotación (Menos Días)")
                st.write("Riesgo de Ruptura")
                high_rot = rotation_df.nsmallest(10, 'rotacion_dias')[['descripcion', 'rotacion_dias', 'avg_inventory_value']]
                st.dataframe(high_rot.style.format({'rotacion_dias': '{:.1f}', 'avg_inventory_value': '${:,.0f}'}))
                
            with col_d2:
                st.subheader("Top 10 Menor Rotación (Más Días)")
                st.write("Posible Sobre-Stock")
                low_rot = rotation_df.nlargest(10, 'rotacion_dias')[['descripcion', 'rotacion_dias', 'avg_inventory_value']]
                st.dataframe(low_rot.style.format({'rotacion_dias': '{:.1f}', 'avg_inventory_value': '${:,.0f}'}))
                
        else:
            st.info("No hay datos de ventas para 2024 para calcular rotación.")
    else:
        st.warning("No hay datos de ventas cargados.")

else:
    st.error("No hay datos de inventario disponibles.")
