# Dashboard API BCCR - SDDE

Aplicación web desarrollada con **Streamlit** para consultar el Sistema de Divulgación de Datos Económicos (SDDE) del Banco Central de Costa Rica (BCCR).

## Requisitos Previos

- Python 3.8+ instalado.
- Token de Autorización de la API del BCCR.

## Instrucciones de Instalación

1. **Vaya al directorio raíz** de este proyecto desde su terminal o consola.
2. (Recomendado) Crear un entorno virtual de Python para el proyecto:
   ```bash
   python -m venv venv
   ```
3. Activar el entorno virtual:
   - En **Windows** (Command Prompt o PowerShell): `.\venv\Scripts\activate`
   - En **Linux/Mac**: `source venv/bin/activate`
4. Instalar las dependencias listadas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Cree un archivo llamado `.env` en la misma ubicación del archivo `app.py`.
2. Pegue el contenido base suministrado en el archivo `.env.example` en su nuevo archivo `.env` y reemplace con su Token real (sin encomillar):
   ```
   BCCR_TOKEN=SuTokenSecretoParaAccederALaAPIBCCR
   ```

## Ejecución

1. Inicie la aplicación escribiendo en la terminal:
   ```bash
   streamlit run app.py
   ```
2. Se abrirá una pestaña en su navegador predeterminado y el panel o *"Dashboard"* estará listo para ser utilizado mediante la interfaz.
