# Análisis de logs para estudiar el comportamiento de los usuarios en una aplicación web de diseño de interiores

Este proyecto incluye configuraciones para procesamiento de datos, visualización con Grafana, notebooks interactivos, y documentación generada con [Quarto](https://quarto.org).

## Estructura del Proyecto

### 📂 `data/`  
  Contiene los datos crudos o procesados necesarios para los análisis.

- **`comunidades.json`**: Lista de comunidades autónomas de España con sus nombres en inglés y español.
  - Campos: `english`, `spanish`

- **`country.json`**: Información de países, incluyendo sus códigos ISO de 2 y 3 letras.
  - Campos: `name`, `let2`, `let3`

- **`geolocalizacion.json`**: Mapeo de direcciones IP a datos geográficos como ciudad, región, país, latitud y longitud.
  - Campos: `city`, `region`, `country`, `lat`, `lng`


### 📂 `grafana_kiosk/`  
 Aplicación Node.js que actúa como un servidor proxy ligero para visualizar dashboards de Grafana en modo kiosk (pantalla completa) dentro de un `iframe`. Útil para exponer visualizaciones limpias en monitores.

 - **`server.js`**: Servidor Express que expone una única ruta (`/`) y sirve una página HTML con un `iframe` apuntando a Grafana en modo kiosk (`/?kiosk`). 

 - **`Dockerfile`**: Permite construir una imagen Docker para desplegar fácilmente el servidor kiosk.


### 📂 `notebooks/`  
  Notebooks interactivos en formato Jupyter con análisis de datos, visualizaciones y modelos. Cada notebook representa una etapa del trabajo analítico del proyecto.

- **`analisis_exploratorio.ipynb`**: Análisis exploratorio inicial de los datos, identificación de patrones, outliers y características relevantes.

- **`clustering.ipynb`**: Implementación y evaluación de técnicas de agrupamiento (K-Means) para identificar segmentos o patrones no supervisados en los datos.

- **`mineria_de_procesos.ipynb`**: Aplicación de técnicas de minería de procesos para entender flujos, secuencias de eventos o comportamientos en los datos.

- **`preprocesamiento.ipynb`**: Transformaciones previas al modelado, como limpieza, extracción de los datos, etc.

- **`preprocesamientossh.py`**: Script de preprocesamiento en Python optimizado para guardar los datos.

- **`reglas_asociacion.ipynb`**: Descubrimiento de reglas de asociación (Apriori) para identificar relaciones frecuentes entre piezas.

- **`serie_temporal.ipynb`**: Análisis de series temporales; incluye modelado, visualización de tendencias, estacionalidad y pronósticos.
### 📂 `paneles/`  
Incluye los dashboards de Grafana en formato JSON, listos para importar. Estos paneles representan visualizaciones diseñadas para diferentes tipos de usuario dentro del sistema.

Contiene:

- **`TFGadmin.json`**: Panel diseñado para usuarios administradores.

- **`TFGfabricante.json`**: Panel orientado a fabricantes .

- **`TFGusuario.json`**: Panel personalizado para usuarios.


### 📄 `_quarto.yml`  
  Archivo de configuración del proyecto Quarto. Define el título del proyecto, opciones de formato, y configuración general para generar la documentación.

### 📄 `docker-compose.yml`  
  Configuración para levantar los servicios (servidores de Grafana, Jupyter y MySQL) usando Docker Compose.
 ```bash
     docker-compose up
```
---
### 📊 Cómo importar paneles en Grafana

Sigue estos pasos para añadir los paneles definidos en los archivos JSON (`TFGadmin.json`, `TFGfabricante.json`, `TFGusuario.json`) a tu instancia de Grafana:

#### Desde la interfaz web

1. Abre tu instancia de Grafana en el navegador.
2. Inicia sesión con el usuario admin.
3. En el menú lateral izquierdo, haz clic en **Dashboards** → **New** → **Import**.
4. Haz clic en **Upload JSON file** y selecciona el archivo deseado desde la carpeta `paneles/`.
5. Haz clic en **Import**.
---

## 📘 ¿Qué es Quarto?

[Quarto](https://quarto.org) es una herramienta de código abierto para crear documentos dinámicos, informes, dashboards y sitios web a partir de código y texto, usando Markdown y Jupyter.

### ¿Qué puedes hacer con Quarto?
- Crear informes reproducibles.
- Generar sitios web o documentos PDF/HTML desde notebooks o Markdown.
- Integrar código en Python, R, Julia y Observable.

---

## ⚙️ ¿Cómo compilar el proyecto Quarto?

1. **Instala Quarto**:  
   [https://quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)

2. **Compilar todo el proyecto**:
     ```bash
     quarto render
     ```

3. **Iniciar un servidor local para vista previa en vivo**:
   ```bash
   quarto preview