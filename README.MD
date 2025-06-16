# Proyecto de Visualización y Análisis de Datos

Este proyecto incluye configuraciones para procesamiento de datos, visualización con Grafana, notebooks interactivos, y documentación generada con [Quarto](https://quarto.org).

## Estructura del Proyecto

- `data/`  
  Contiene los datos crudos o procesados necesarios para los análisis.

- `grafana_kiosk/`  
  Archivos relacionados con la visualización en modo kiosco de Grafana (paneles configurados para pantalla completa).

- `logs/`  
  Carpeta donde se almacenan los registros del sistema o del proyecto para fines de diagnóstico.

- `notebooks/`  
  Notebooks interactivos (probablemente en Jupyter o Quarto) con análisis de datos, visualizaciones y pruebas.

- `.gitignore`  
  Archivo que indica qué archivos o carpetas deben ser ignorados por Git.

- `_quarto.yml`  
  Archivo de configuración del proyecto Quarto. Define el título del proyecto, opciones de formato, y configuración general para generar la documentación.

- `docker-compose.yml`  
  Configuración para levantar los servicios (por ejemplo, servidores de Grafana, Jupyter u otros) usando Docker Compose.

---

## 📘 ¿Qué es Quarto?

[Quarto](https://quarto.org) es una herramienta de código abierto para crear documentos dinámicos, informes, dashboards y sitios web a partir de código y texto, usando Markdown, Jupyter o R Markdown.

### ¿Qué puedes hacer con Quarto?
- Crear informes reproducibles.
- Generar sitios web o documentos PDF/HTML desde notebooks o Markdown.
- Integrar código en Python, R, Julia y Observable.

---

## ⚙️ ¿Cómo compilar el proyecto Quarto?

1. **Instala Quarto** (si no lo tienes):  
   👉 [https://quarto.org/docs/get-started/](https://quarto.org/docs/get-started/)

2. **Compilar un archivo específico o todo el proyecto**:

   - Para renderizar todo el proyecto:
     ```bash
     quarto render
     ```

   - Para renderizar un archivo específico:
     ```bash
     quarto render tu_archivo.qmd
     ```

3. **Opcional: iniciar un servidor local para vista previa en vivo**:
   ```bash
   quarto preview