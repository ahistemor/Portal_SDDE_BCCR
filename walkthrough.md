# Documentación General del Proyecto: Portal SDDE BCCR

Este documento engloba todas las características implementadas desde el inicio de nuestro desarrollo hasta la versión actual del Dashboard Económico.

## 1. Arquitectura y Consumo de la API (Backend)
- **Bypass de Seguridad (Azure WAF):** Inicialmente el Banco Central bloqueaba las solicitudes automatizadas devolviendo un `Error 403 Forbidden`. Solucionamos esto implementando cabeceras (`headers`) personalizadas simulando un navegador web legítimo.
- **Aplanamiento Recursivo de JSON:** Los datos venían en estructuras profundamente anidadas (datos -> indicadores -> series). Creamos un algoritmo inteligente en `utils.py` capaz de desempaquetar cualquier nivel de profundidad de manera recursiva hasta convertirlo en un `DataFrame` tabular perfecto.
- **Consultas Múltiples:** Se agregó soporte para buscar varios códigos simultáneamente usando separaciones por comas.

## 2. Experiencia de Usuario y Visualización (Frontend)
- **Diseño en Streamlit:** Se desarrolló una aplicación limpia con una barra lateral de opciones y selectores de idiomas y fechas.
- **Botones de Consulta Rápida:** Implementamos atajos de un solo clic para cargar los indicadores más comunes de Costa Rica (Dólar, Inflación, Tasa Básica Pasiva y Euro).
- **Gráficos Dinámicos con Plotly:** El sistema dibuja automáticamente gráficos interactivos. Permite al usuario renombrar las leyendas, títulos y ejes en tiempo real sin necesidad de recargar la página.

## 3. Inteligencia Artificial (El Economista Virtual)
- **Resumen Estadístico Inteligente:** Para proteger tu facturación de la API y evitar saturar la memoria de lectura del LLM, el sistema comprime miles de registros en un resumen estadístico (valores extremos, promedio y tendencia general).
- **Streaming de OpenAI:** Integrado directamente al Dashboard mediante una conexión API. Al pulsar el botón, una Inteligencia Artificial redacta en vivo un reporte profesional evaluando el comportamiento numérico y sus posibles impactos macroeconómicos para Costa Rica.

## 4. Gestión de Layout Dinámico
- El sistema cuenta con inteligencia contextual: si solicitas "Metadata", la interfaz se limpia escondiendo los gráficos e IA, mostrando solo la opción de Exportar a Excel. 
- Si solicitas "Series Temporales", despliega automáticamente tres pestañas interactivas: 🗂️ Datos, 📊 Gráfico y 🤖 Análisis IA.
