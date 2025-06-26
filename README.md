
# 🛠️ Comparador de Parámetros Generales: SFERE vs TiCares

Aplicación interactiva en Streamlit que permite visualizar, explorar y comparar los parámetros generales de configuración entre los sistemas **SFERE** y **TiCares**, facilitando así su análisis técnico y funcional.

---

## 📌 Definición Funcional

### Objetivo
La aplicación permite:
- Visualizar todos los parámetros generales existentes en **TiCares** y **SFERE**.
- Identificar qué parámetros están:
  - Solo en **TiCares**
  - Solo en **SFERE**
  - En **ambos sistemas**
- Consultar el valor por defecto de cada parámetro.
- Analizar el detalle del valor del parámetro según organización, centro y servicio.
- Comparar en detalle los valores definidos para cada sistema y detectar diferencias.

### Casos de Uso
- Validación de migraciones o sincronización de configuraciones entre sistemas.
- Auditoría de coherencia de parámetros.
- Apoyo para equipos funcionales y técnicos en tareas de homologación de entornos.

---

## ⚙️ Definición Técnica

### Tecnologías utilizadas
- **Python 3.10+**
- **Streamlit** para la interfaz web
- **Pandas** para análisis de datos
- **Plotly** para visualización interactiva
- **Excel (XLSX)** como salida complementaria

### Estructura de la aplicación
- Carga de datos desde un archivo CSV con separador `;`
- Identificación de parámetros por su código (`CODIGOPARAMETRO`)
- Separación lógica de los parámetros en tres grupos:
  - Solo en TiCares
  - Solo en SFERE
  - En ambos sistemas
- Visualización de:
  - Distribución global mediante gráfico apilado
  - Listado de parámetros por grupo
  - Filtro por código para análisis individual
  - Detalle completo por centro, organización y servicio
- Comparación detallada con marcado visual de coincidencias (`Coincide: Sí / No`)

### Estructura esperada del CSV
El archivo de entrada debe contener las siguientes columnas:

```csv
CODIGOPARAMETRO;DESCRIPCIONPARAMETRO;VALORPORDEFECTO;VALORPORCENTRO;ORGANIZACION;CENTRO;SERVICIO;FUENTE
```

Donde:
- `FUENTE` debe tener los valores `TICARES` o `SFERE`.

---

## 📂 Salida en Excel

La aplicación puede generar un Excel con 4 hojas:
1. **Solo_TICARES**: parámetros exclusivos de TiCares (con código, descripción y valor por defecto).
2. **Solo_SFERE**: parámetros exclusivos de SFERE.
3. **Comunes**: parámetros presentes en ambos sistemas.
4. **Comparativa_Detallada**: comparación lado a lado de los valores por defecto y por centro con una columna `COINCIDE` (`Sí/No`) para destacar diferencias.

---

## ▶️ Ejecución en local
Importa el código en tu entorno de desarrollo.

Instala dependencias si es necesario:

```bash
pip install streamlit pandas plotly openpyxl
```

Ejecuta la app (si quieres arrancar en local):

```bash
streamlit run app.py
```

---

## ▶️ Ejecución en la web
Abrir el navegador y acceder al siguiente enlace: https://getronics-parameterscomparator.streamlit.app/


## ✅ Autoría

Desarrollado por el equipo de Getronics para apoyar la revisión y mantenimiento de parámetros generales en entornos críticos de información hospitalaria.
