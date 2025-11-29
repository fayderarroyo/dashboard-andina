import pandas as pd
import os

data_dir = r"C:\Users\Fayder Arroyo Herazo\Desktop\Estadistica Especializacion\Electiva1\proyecto final electiva"

files = [
    "clientes_andina.csv",
    "importaciones_andina (1).xlsx",
    "inventario_andina.csv",
    "productos_andina.csv",
    "ventas_andina.csv"
]

for f in files:
    path = os.path.join(data_dir, f)
    print(f"--- {f} ---")
    try:
        if f.endswith('.xlsx'):
            df = pd.read_excel(path)
        else:
             # Trying common encodings/separators for Spanish data
            try:
                df = pd.read_csv(path, encoding='latin1', sep=';')
                if len(df.columns) <= 1:
                     df = pd.read_csv(path, encoding='utf-8', sep=',')
            except:
                 df = pd.read_csv(path, encoding='utf-8', sep=',')

        print(df.info())
        print(df.head())
    except Exception as e:
        print(f"Error reading {f}: {e}")
    print("\n")
