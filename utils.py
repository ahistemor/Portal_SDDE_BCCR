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

def generate_statistical_summary(df):
    """
    Genera un resumen estadístico de un DataFrame de series temporales para ahorrar
    tokens al enviarlo a un LLM.
    """
    if df.empty:
        return "El conjunto de datos está vacío."
        
    summary = []
    
    # Intentar buscar columnas agrupadoras (nombre del indicador)
    color_col = None
    for c in ["nombreIndicador", "codigoIndicador", "titulo"]:
        if c in df.columns:
            color_col = c
            break
            
    # Intentar buscar columnas de valor
    val_col = "valorDatoPorPeriodo" if "valorDatoPorPeriodo" in df.columns else None
    if not val_col:
        # buscar la primera columna numérica
        for c in df.select_dtypes(include=['number']).columns:
            val_col = c
            break
            
    # Intentar buscar la fecha
    date_col = "fecha" if "fecha" in df.columns else None

    if not val_col:
        return "No se detectaron valores numéricos para resumir."
        
    series_groups = df[color_col].unique() if color_col else ["Serie Única"]
    
    for serie in series_groups:
        if color_col:
            df_subset = df[df[color_col] == serie].copy()
        else:
            df_subset = df.copy()
            
        if date_col:
            df_subset[date_col] = pd.to_datetime(df_subset[date_col], errors='coerce')
            df_subset = df_subset.sort_values(date_col).dropna(subset=[date_col, val_col])
        else:
            df_subset = df_subset.dropna(subset=[val_col])
            
        if df_subset.empty:
            continue
            
        val_min = df_subset[val_col].min()
        val_max = df_subset[val_col].max()
        val_mean = df_subset[val_col].mean()
        
        primer_registro = df_subset.iloc[0]
        ultimo_registro = df_subset.iloc[-1]
        
        tendencia = "Al alza" if ultimo_registro[val_col] > primer_registro[val_col] else "A la baja"
        if abs(ultimo_registro[val_col] - primer_registro[val_col]) < (val_mean * 0.01):
            tendencia = "Estable"
            
        reporte = f"--- Indicador: {serie} ---\n"
        if date_col:
            reporte += f"Periodo: Desde {primer_registro[date_col].strftime('%Y-%m-%d')} hasta {ultimo_registro[date_col].strftime('%Y-%m-%d')}\n"
        reporte += f"Valor inicial: {primer_registro[val_col]:.4f}\n"
        reporte += f"Valor final: {ultimo_registro[val_col]:.4f}\n"
        reporte += f"Mínimo histórico del periodo: {val_min:.4f}\n"
        reporte += f"Máximo histórico del periodo: {val_max:.4f}\n"
        reporte += f"Promedio del periodo: {val_mean:.4f}\n"
        reporte += f"Tendencia general observada: {tendencia}\n"
        
        summary.append(reporte)
        
    return "\n".join(summary)
