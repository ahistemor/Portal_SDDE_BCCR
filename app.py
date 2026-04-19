import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

from api_client import (
    descargar_cuadros, metadata_cuadro, series_cuadro,
    descargar_indicadores, metadata_indicador, series_indicador,
    BCCRAPIError
)
from utils import format_json_to_dataframe, convert_df_to_excel

# Cargar variables de entorno
load_dotenv()

st.set_page_config(page_title="Dashboard SDDE - BCCR", layout="wide")

st.title("Sistema de Divulgación de Datos Económicos (SDDE)")
st.subheader("Banco Central de Costa Rica")

# ==========================================
# Barra lateral: Configuración y Selección
# ==========================================
st.sidebar.header("Configuración de Consulta")

# Selector de endpoint
ENDPOINTS = {
    "descargar_catalogo_cuadros": "Descargar Catálogo de Cuadros",
    "metadata_cuadro": "Metadata de Cuadro",
    "series_cuadro": "Series de Cuadro",
    "descargar_catalogo_indicadores": "Descargar Catálogo de Indicadores Económicos",
    "metadata_indicador": "Metadata de Indicador Económico",
    "series_indicador": "Series de Indicador Económico",
}
selected_endpoint_key = st.sidebar.selectbox(
    "Seleccione el Endpoint", 
    options=list(ENDPOINTS.keys()), 
    format_func=lambda x: ENDPOINTS[x]
)

# Idioma (siempre requerido, excepto si no es de API)
idioma = st.sidebar.radio("Idioma", options=["ES", "EN"], index=0)

# ==========================================
# Lógica de visibilidad de controles
# ==========================================
req_codigo = selected_endpoint_key in ["metadata_cuadro", "series_cuadro", "metadata_indicador", "series_indicador"]
req_fechas = selected_endpoint_key in ["series_cuadro", "series_indicador"]

codigo = ""
fecha_inicio = None
fecha_fin = None

if req_codigo:
    # Estado inicial si no existe
    if "input_codigo" not in st.session_state:
        st.session_state.input_codigo = ""

    if selected_endpoint_key in ["metadata_cuadro", "series_cuadro"]:
        st.sidebar.markdown("**Consultas Rápidas**")
        c1, c2 = st.sidebar.columns(2)
        if c1.button("Dólar (1)"):
            st.session_state.input_codigo = "1"
        if c2.button("Inflación (51)"):
            st.session_state.input_codigo = "51"
            
    elif selected_endpoint_key in ["metadata_indicador", "series_indicador"]:
        st.sidebar.markdown("**Consultas Rápidas**")
        c1, c2 = st.sidebar.columns(2)
        if c1.button("TBP (423)"):
            st.session_state.input_codigo = "423"
        if c2.button("Euro (333)"):
            st.session_state.input_codigo = "333"

    codigo = st.sidebar.text_input(
        "Código(s) (Requerido)", 
        key="input_codigo",
        help="Puede usar comas para consultar múltiples códigos a la vez. Ej: 317, 318"
    )

if req_fechas:
    fecha_inicio = st.sidebar.date_input("Fecha Inicio (Requerido)")
    fecha_fin = st.sidebar.date_input("Fecha Fin (Requerido)")
    
# Botón para ejecutar consulta
ejecutar = st.sidebar.button("Ejecutar Consulta", type="primary")

# ==========================================
# Ejecución de la consulta
# ==========================================
if ejecutar:
    # Validaciones básicas antes de consultar
    errores_validacion = []
    
    if req_codigo and not codigo.strip():
        errores_validacion.append("El campo 'Código' es obligatorio para la consulta seleccionada.")
    if req_fechas and not fecha_inicio:
         errores_validacion.append("La 'Fecha Inicio' es obligatoria.")
    if req_fechas and not fecha_fin:
         errores_validacion.append("La 'Fecha Fin' es obligatoria.")
    
    if errores_validacion:
         for error in errores_validacion:
             st.error(error)
    else:
         with st.spinner("Consultando a la API del BCCR..."):
             try:
                 resultado = None
                 
                 # Mapear la consulta según el endpoint seleccionado
                 if selected_endpoint_key == "descargar_catalogo_cuadros":
                     resultado = descargar_cuadros(idioma=idioma)
                 elif selected_endpoint_key == "descargar_catalogo_indicadores":
                     resultado = descargar_indicadores(idioma=idioma)
                 else:
                     # Endpoints iterables por código
                     lista_codigos = [c.strip() for c in codigo.split(',')]
                     todos_los_datos = []
                     
                     for cod in lista_codigos:
                         if not cod: continue
                         if selected_endpoint_key == "metadata_cuadro":
                             res = metadata_cuadro(cod, idioma=idioma)
                         elif selected_endpoint_key == "series_cuadro":
                             fi_str = fecha_inicio.strftime('%Y/%m/%d')
                             ff_str = fecha_fin.strftime('%Y/%m/%d')
                             res = series_cuadro(cod, fi_str, ff_str, idioma=idioma)
                         elif selected_endpoint_key == "metadata_indicador":
                             res = metadata_indicador(cod, idioma=idioma)
                         elif selected_endpoint_key == "series_indicador":
                             fi_str = fecha_inicio.strftime('%Y/%m/%d')
                             ff_str = fecha_fin.strftime('%Y/%m/%d')
                             res = series_indicador(cod, fi_str, ff_str, idioma=idioma)
                             
                         # Acumular la carga útil
                         if res and not res.get("is_file"):
                             todos_los_datos.append(res["data"])
                     
                     if todos_los_datos:
                         resultado = {"is_file": False, "data": todos_los_datos}
                 
                 # Procesar y guardar al estado de sesión
                 if resultado:
                     st.session_state.selected_endpoint_key = selected_endpoint_key
                     st.session_state.idioma = idioma
                     st.session_state.mostrar_grafico = False
                     
                     if resultado.get("is_file"):
                         st.session_state.is_file = True
                         st.session_state.file_content = resultado["content"]
                     else:
                         st.session_state.is_file = False
                         df = format_json_to_dataframe(resultado["data"])
                         st.session_state.df_resultado = df
                         st.session_state.excel_data = convert_df_to_excel(df) if not df.empty else None
                         
                     st.success("Consulta ejecutada y almacenada con éxito.")
                     
             except ValueError as ve:
                 st.error(f"Error de Configuración: {ve}")
             except BCCRAPIError as api_err:
                 st.error(f"Error de la API: {api_err}")
             except Exception as ex:
                 st.error(f"Error inesperado: {ex}")

# ==========================================
# Despliegue de Datos Estables (fuera del botón de ejecución)
# ==========================================
if "selected_endpoint_key" in st.session_state:
    endpoint_key = st.session_state.selected_endpoint_key
    idioma_res = st.session_state.idioma
    
    if st.session_state.get("is_file"):
         st.write(f"### Descarga de Catálogo ({ENDPOINTS[endpoint_key]})")
         st.download_button(
             label="Descargar Archivo Excel",
             data=st.session_state.file_content,
             file_name=f"catalogo_{endpoint_key}_{idioma_res}.xlsx",
             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
         )
    else:
         df = st.session_state.get("df_resultado")
         if df is not None and not df.empty:
             st.write(f"### Resultados ({ENDPOINTS[endpoint_key]})")
             
             # 1. Movidos los botones justo debajo del título
             col_btn1, col_btn2 = st.columns(2)
             with col_btn1:
                 st.download_button(
                     label="Exportar a Excel",
                     data=st.session_state.excel_data,
                     file_name=f"resultados_{endpoint_key}.xlsx",
                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                 )
             with col_btn2:
                 if "series" in endpoint_key:
                     label_boton = "Ocultar Gráfico" if st.session_state.get("mostrar_grafico", False) else "Generar Gráfico"
                     if st.button(label_boton, type="secondary"):
                         st.session_state.mostrar_grafico = not st.session_state.get("mostrar_grafico", False)
                         st.rerun()
                 else:
                     st.info("La función gráfica está optimizada para Series.")

             st.write("---")

             # 2 y 3. Sistema tipo acordeón (Tabs) si se acciona el gráfico
             if st.session_state.get("mostrar_grafico"):
                 # Tab 1 es Gráfico (aparecerá primero), Tab 2 es la Tabla
                 tab_grafico, tab_datos = st.tabs(["📊 Gráfico Interactivo", "🗂️ Datos en Tabla"])
                 
                 with tab_grafico:
                     st.write("### Opciones de Gráfico")
                     
                     x_options = list(df.columns)
                     y_options = list(df.columns)
                     
                     def_x = "fecha" if "fecha" in df.columns else x_options[0]
                     def_y = "valorDatoPorPeriodo" if "valorDatoPorPeriodo" in df.columns else y_options[-1]
                     
                     color_col = None
                     for c in ["nombreIndicador", "codigoIndicador", "titulo"]:
                         if c in df.columns:
                             color_col = c
                             break
                             
                     colA, colB, colC = st.columns(3)
                     titulo = colA.text_input("Título del Gráfico", value=f"Evolución - {ENDPOINTS[endpoint_key]}")
                     eje_x = colB.text_input("Etiqueta Eje X", value=def_x.capitalize())
                     eje_y = colC.text_input("Etiqueta Eje Y", value=def_y.capitalize())
                     
                     colD, colE = st.columns(2)
                     x_col = colD.selectbox("Columna Datos Eje X", options=x_options, index=x_options.index(def_x))
                     y_col = colE.selectbox("Columna Datos Eje Y", options=y_options, index=y_options.index(def_y))
                     
                     import plotly.express as px
                     
                     if color_col:
                         series_unicas = df[color_col].dropna().unique().tolist()
                         series_seleccionadas = st.multiselect("Series a mostrar:", options=series_unicas, default=series_unicas)
                         
                         df_plot = df[df[color_col].isin(series_seleccionadas)].copy()
                         
                         if series_seleccionadas:
                             st.write("**Personalizar nombre de series (Leyenda):**")
                             numero_columnas_renombramiento = min(len(series_seleccionadas), 4)
                             cols_renombrar = st.columns(numero_columnas_renombramiento)
                             nombres_series_config = {}
                             
                             for idx, serie in enumerate(series_seleccionadas):
                                 col_idx = idx % numero_columnas_renombramiento
                                 nuevo = cols_renombrar[col_idx].text_input(f"Nombre para: {serie}", value=str(serie), key=f"ser_{idx}")
                                 nombres_series_config[serie] = nuevo
                                 
                             df_plot[color_col] = df_plot[color_col].replace(nombres_series_config)
                             
                         fig = px.line(df_plot, x=x_col, y=y_col, color=color_col, title=titulo, markers=True)
                     else:
                         df_plot = df.copy()
                         fig = px.line(df_plot, x=x_col, y=y_col, title=titulo, markers=True)
                         
                     fig.update_layout(xaxis_title=eje_x, yaxis_title=eje_y)
                     st.plotly_chart(fig, use_container_width=True)

                 with tab_datos:
                     st.dataframe(df, use_container_width=True)
             else:
                 # Si el panel gráfico no está activo, simplemente mostramos la tabla normal
                 st.dataframe(df, use_container_width=True)
         else:
             st.info("La API no devolvió datos estructurados para procesar.")
