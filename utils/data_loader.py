import pandas as pd
import os

# Define data directory
DATA_DIR = r"C:\Users\Fayder Arroyo Herazo\Desktop\Estadistica Especializacion\Electiva1\proyecto final electiva"

def load_data():
    """
    Loads all data files and returns a dictionary of DataFrames.
    """
    files = {
        "ventas": "ventas_andina.csv",
        "clientes": "clientes_andina.csv",
        "productos": "productos_andina.csv",
        "cartera": "cartera_andina.csv",
        "inventario": "inventario_andina.csv",
        "importaciones": "importaciones_andina (1).xlsx"
    }
    
    data = {}
    
    for key, filename in files.items():
        path = os.path.join(DATA_DIR, filename)
        try:
            if filename.endswith('.xlsx'):
                df = pd.read_excel(path)
            else:
                # Try reading with different encodings/separators
                try:
                    df = pd.read_csv(path, encoding='latin1', sep=';')
                    if len(df.columns) <= 1:
                         df = pd.read_csv(path, encoding='utf-8', sep=',')
                except:
                     df = pd.read_csv(path, encoding='utf-8', sep=',')
            
            data[key] = df
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            data[key] = pd.DataFrame() # Return empty DF on error
            
    return data

def process_data(data):
    """
    Processes and merges data to create a central data model.
    """
    ventas = data.get("ventas")
    clientes = data.get("clientes")
    productos = data.get("productos")
    
    if ventas is None or ventas.empty:
        return data
        
    # Convert dates
    date_cols = ['fecha']
    for col in date_cols:
        if col in ventas.columns:
            ventas[col] = pd.to_datetime(ventas[col], errors='coerce')
            
    # Merge Ventas with Clientes and Productos
    # Ensure IDs are same type
    if clientes is not None and not clientes.empty:
        ventas['cliente_id'] = ventas['cliente_id'].astype(str)
        clientes['cliente_id'] = clientes['cliente_id'].astype(str)
        ventas = ventas.merge(clientes, on='cliente_id', how='left')
        
    if productos is not None and not productos.empty:
        ventas['producto_id'] = ventas['producto_id'].astype(str)
        productos['producto_id'] = productos['producto_id'].astype(str)
        ventas = ventas.merge(productos, on='producto_id', how='left')
        
    # Calculate Margins if not present (though inspect showed 'margen_total_cop')
    # Ensure numeric columns are numeric
    numeric_cols = ['subtotal_cop', 'margen_total_cop', 'costo_unitario_est_cop']
    for col in numeric_cols:
        if col in ventas.columns:
             # Remove currency symbols if string
            if ventas[col].dtype == 'object':
                 ventas[col] = pd.to_numeric(ventas[col].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce')
    
    # Calculate Margin %
    if 'subtotal_cop' in ventas.columns and 'margen_total_cop' in ventas.columns:
        ventas['margen_pct'] = (ventas['margen_total_cop'] / ventas['subtotal_cop']) * 100
        
    data['merged_ventas'] = ventas
    
    # Process Cartera dates
    cartera = data.get("cartera")
    if cartera is not None and not cartera.empty:
        cartera['fecha_factura'] = pd.to_datetime(cartera['fecha_factura'], errors='coerce')
        cartera['fecha_vencimiento'] = pd.to_datetime(cartera['fecha_vencimiento'], errors='coerce')
        
    return data
