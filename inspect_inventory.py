import pandas as pd
import os

data_dir = r"C:\Users\Fayder Arroyo Herazo\Desktop\Estadistica Especializacion\Electiva1\proyecto final electiva"
path = os.path.join(data_dir, "inventario_andina.csv")

try:
    df = pd.read_csv(path, encoding='latin1', sep=';')
    if len(df.columns) <= 1:
            df = pd.read_csv(path, encoding='utf-8', sep=',')
    
    print("Columns:", list(df.columns))
    print("Unique Dates:", df['fecha_corte'].unique())
    print(df.head())
    print(df.info())
except Exception as e:
    print(f"Error: {e}")
