import pandas as pd
import io

import json

def format_json_to_dataframe(json_data):
    """
    Intenta aplanar el JSON y convertirlo en un DataFrame de Pandas para visualización,
    extrayendo iterativamente todas las listas anidadas (datos -> indicadores -> series).
    """
    if not json_data:
        return pd.DataFrame()
        
    try:
        # En caso de que la respuesta sea un string escapado que contiene JSON
        if isinstance(json_data, str):
            try: json_data = json.loads(json_data)
            except: pass

        if isinstance(json_data, dict):
            json_data = [json_data]
            
        if isinstance(json_data, list):
            df = pd.json_normalize(json_data)
            
            # Buscar columnas que contengan listas (para expandir las series repetidamente)
            while True:
                found_list = False
                for col in df.columns:
                    valid_items = df[col].dropna()
                    if valid_items.empty: continue
                        
                    first_item = valid_items.iloc[0]
                    
                    if isinstance(first_item, str) and first_item.strip().startswith('[') and first_item.strip().endswith(']'):
                        try:
                            df[col] = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
                            first_item = df[col].dropna().iloc[0]
                        except: pass

                    if isinstance(first_item, list):
                        found_list = True
                        df = df.explode(col)
                        df = df.reset_index(drop=True)
                        
                        exploded_items = df[col].dropna()
                        # Si desempaquetamos y hay diccionarios adentros, expandimos
                        if not exploded_items.empty and isinstance(exploded_items.iloc[0], dict):
                            safe_list = [x if isinstance(x, dict) else {} for x in df[col]]
                            expanded_cols = pd.json_normalize(safe_list)
                            
                            # Prevenir colision de nombres de metadatos si tienen llaves duplicadas en multiniveles
                            overlap = set(df.columns) & set(expanded_cols.columns)
                            if overlap:
                                expanded_cols = expanded_cols.rename(columns={c: f"{c}_nivel" for c in overlap})
                                
                            df = df.drop(columns=[col]).join(expanded_cols)
                        break
                        
                # Si exploramos todas las columnas y ya es 100% plana
                if not found_list:
                    break
                    
            return df
            
    except Exception as e:
        return pd.DataFrame([{"Error de Parseo": str(e), "Raw Data": str(json_data)}])
        
    return pd.DataFrame([{"Raw Data": str(json_data)}])

def convert_df_to_excel(df):
    """
    Toma un DataFrame y devuelve un archivo Excel en memoria (bytes).
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    processed_data = output.getvalue()
    return processed_data
