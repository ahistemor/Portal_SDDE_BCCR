# Integración de Asistente de IA (Generador de Informes Económicos)

Este plan detalla cómo agregar la capacidad de análisis con Inteligencia Artificial directamente en tu Dashboard de Streamlit para interpretar los datos del BCCR.

## User Review Required

> [!IMPORTANT]
> **El uso de MCP vs API Directa:**
> Mencionaste utilizar el protocolo MCP (Model Context Protocol). MCP está diseñado para cuando quieres que un LLM *externo* (como Claude Desktop) se conecte a tus herramientas. Dado que quieres que la experiencia viva **"dentro del mismo dashboard"** de Streamlit, la arquitectura más limpia, rápida y profesional es conectar el Dashboard **directamente a la API de OpenAI** (o cualquier otro proveedor LLM) por detrás. De esta forma, el Dashboard ya tiene los datos en su memoria (la tabla generada) y se los pasa como contexto a la IA sin necesidad de montar un servidor MCP intermedio. ¿Estás de acuerdo con seguir la ruta de conexión directa mediante API para integrarlo nativamente en la web?

> [!WARNING]
> **Límites de Tokens:**
> Las series de tiempo pueden tener miles de filas (ej. Tipo de Cambio diario por 10 años). Enviar esto crudo a la IA es costoso y lento. Mi propuesta es que el código calcule un "resumen matemático inteligente" de forma automática antes de enviarlo (fecha de inicio, fecha de fin, valor inicial, valor final, mínimo, máximo, y tendencia) para que la IA haga su informe económico cualitativo de la variable sin desbordar su límite de lectura. ¿Estás de acuerdo?

## Proposed Changes

### Archivos de Configuración
#### [MODIFY] `requirements.txt`
- Agregar la librería oficial `openai` para la conexión con el modelo (en caso de usar ChatGPT).

#### [MODIFY] `.env.example` y Entorno
- Agregar la variable de entorno `OPENAI_API_KEY=` para dejar claro dónde debe ir la llave.

---

### UI y Lógica Principal
#### [MODIFY] `app.py`
- **Botón de Acción:** En la misma zona donde están "Exportar a Excel" y "Generar Gráfico", agregaremos un tercer botón **"🤖 Analizar con IA"**.
- **Nueva Pestaña (Tab):** Si se acciona, el componente principal pasará a tener tres pestañas:
  1. `📊 Gráfico Interactivo`
  2. `🗂️ Datos en Tabla`
  3. `🤖 Análisis Económico (IA)`
- **Procesamiento de LLM:** Cuando el usuario entra a la pestaña de IA, el código recolectará la metadata del indicador que se consultó (nombre, valores relevantes resumidos) y llamará al modelo pasándole el contexto. El prompt le pedirá que actúe como un Analista Económico.
- **Flujo en Vivo:** Se implementará el sistema de "streaming" de Streamlit para que el texto del análisis aparezca letra por letra en la interfaz, exactamente como ocurre en ChatGPT, dando una sensación totalmente Premium.

## Verification Plan

### Manual Verification
1. Ingresaremos tu API Key de OpenAI (o el servicio que dispongas) en el archivo `.env`.
2. Lanzarás una consulta en la plataforma (ej. Tasa Básica Pasiva).
3. Seleccionarás "Analizar con IA".
4. Verificaremos que la IA recibe correctamente el nombre del indicador, detecta sus valores máximos/mínimos y es capaz de redactar de vuelta una hipótesis económica válida en la interfaz web de manera fluida.
