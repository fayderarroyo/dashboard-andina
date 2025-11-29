import streamlit as st
import pandas as pd
from utils.data_loader import load_data, process_data

st.set_page_config(
    page_title="Comercializadora Andina BI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Inteligencia de Negocios - Comercializadora Andina SAS")

st.markdown("""
Bienvenido al sistema de información gerencial. Utilice el menú lateral para navegar entre las diferentes vistas de análisis.

### Módulos Disponibles:

1.  **Panorama General**: Visión consolidada de Ventas y Margen.
2.  **Rentabilidad Detallada**: Análisis por Portafolio, Región y Canal.
3.  **Gestión de Clientes**: Segmentación, Concentración y Valor.
4.  **Importaciones y Costos**: Seguimiento de compras internacionales y TRM.
5.  **Inventario y Operación**: Rotación de stock y eficiencia operativa.
6.  **Riesgo de Crédito**: Estado de la cartera y gestión de cobros.
""")

# Load data once and cache it (Streamlit caching could be added to data_loader)
with st.spinner('Cargando datos...'):
    raw_data = load_data()
    data = process_data(raw_data)
    st.session_state['data'] = data

st.success("Datos cargados correctamente. Seleccione una página en el menú lateral.")
