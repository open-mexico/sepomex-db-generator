# 🇲🇽 MexPost Data
# Base de Datos de Códigos Postales y GeoJSON de México (SEPOMEX)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Optimized-lightgrey.svg)](https://www.sqlite.org/)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![LinkedIn][linkedin-shield]][linkedin-url]


Generador ETL automatizado para descargar, normalizar y cruzar el catálogo oficial de **Códigos Postales de México (SEPOMEX)** con polígonos geoespaciales (GeoJSON). Produce bases de datos SQLite relacionales, con índices espaciales, centroides calculados y auditoría de cobertura geográfica — listas para producción en segundos.

---

## 🌍 Abstract (English)

`sepomex-db-generator` is an open-source ETL (Extract, Transform, Load) pipeline that turns Mexico's official SEPOMEX postal catalog into two production-ready SQLite databases: a lightweight relational version for fast postal lookups, and a full spatial version enriched with GeoJSON polygons, bounding boxes, and centroids for each postal code.

Key capabilities: high-performance batch loading with optimized SQLite PRAGMAs, spatial indexing for reverse geocoding, deterministic duplicate-polygon resolution, and an automatic audit log of postal codes missing geographic coverage.

## 📄 Resumen (Español)

`sepomex-db-generator` es un pipeline ETL de código abierto que convierte el catálogo oficial de SEPOMEX en dos bases de datos SQLite listas para producción: una versión relacional ligera para autocompletados y búsquedas postales, y una versión espacial enriquecida con polígonos GeoJSON, bounding boxes y centroides por código postal.

Incluye: carga masiva optimizada con PRAGMAs de SQLite, índices espaciales para geocodificación inversa, resolución determinista de polígonos duplicados y un log de auditoría automático para códigos postales sin cobertura geográfica.

---

## 🎯 Objetivo

Proporcionar una fuente de verdad **reproducible**, **actualizable** y **lista para integración** sobre la división postal de México. En lugar de distribuir bases de datos estáticas y desactualizadas, este proyecto entrega el *motor* para regenerar la base de datos desde la fuente oficial en cualquier momento, garantizando datos frescos para microservicios, aplicaciones de logística, sistemas GIS y ciencia de datos.

---

## ✨ Características Principales

* **Extracción Automatizada:** Descarga directa del catálogo oficial más reciente de Correos de México (SEPOMEX), sin intervención manual.
* **Normalización Relacional:** Divide los datos planos en 3 tablas optimizadas — `estados`, `municipios` y `colonias` — eliminando duplicados y estandarizando identificadores.
* **Inyección Espacial:** Vincula automáticamente los polígonos GeoJSON a cada código postal, almacenando geometría, bounding box (`min_lat`, `max_lat`, `min_lon`, `max_lon`) y centroide (`centro_lat`, `centro_lon`) por cada registro.
* **Resolución de Duplicados:** Cuando un mismo código postal aparece en múltiples archivos GeoJSON, conserva siempre el polígono más completo (con bounding box válido), garantizando integridad de datos.
* **Índices de Alto Rendimiento:** Creados *después* de la carga masiva para máxima velocidad. Incluye índices simples, compuestos (`COLLATE NOCASE`) y espaciales (bbox, centroide, cobertura geométrica) — búsquedas en milisegundos sobre millones de registros.
* **Carga Batch Optimizada:** Configuración de SQLite (`PRAGMA journal_mode`, `synchronous`, `temp_store`, `cache_size`) y uso de `method=multi` + `chunksize` en pandas para inserciones masivas de máximo rendimiento.
* **Log de Auditoría Geográfica:** Genera automáticamente `dist/db_geo_errores.log` con los códigos postales que no tienen polígono asignado, incluyendo timestamp por ejecución, para facilitar auditorías de cobertura.
* **Bases de Datos Dual:** `db_postal.sqlite` (relacional ligera, ideal para autocompletado y búsquedas web) y `db_geo.sqlite` (texto + geometría GeoJSON, ideal para geocodificación inversa y renderizado de mapas).
* **Arquitectura Modular:** Código organizado en módulos independientes (`extract`, `transform`, `load`, `utils`) con responsabilidades claras y pruebas unitarias automatizadas con `pytest`.

---

## 🗂️ Esquema de Base de Datos

### Tablas relacionales (ambas bases de datos)

| Tabla | Columnas clave | Descripción |
|---|---|---|
| `estados` | `id`, `nombre` | 32 entidades federativas de México |
| `municipios` | `id`, `nombre`, `estado_id`, `nombre_normalizado` | Municipios vinculados a su estado |
| `colonias` | `codigo`, `nombre`, `tipo`, `ciudad`, `zona`, `estado_id`, `municipio_id`, `nombre_normalizado` | Asentamientos con su código postal |

### Columnas adicionales en `db_geo.sqlite`

| Columna | Tipo | Descripción |
|---|---|---|
| `geometria` | TEXT (JSON) | Polígono GeoJSON del código postal |
| `min_lon`, `min_lat`, `max_lon`, `max_lat` | REAL | Bounding box para geocodificación inversa |
| `centro_lon`, `centro_lat` | REAL | Centroide calculado para búsquedas de cercanía |

---

## 🛠️ Tecnologías

* **Python 3.12+** — Lenguaje principal del pipeline ETL
* **Pandas** — Normalización, limpieza y carga masiva de datos
* **SQLite3** — Motor de base de datos embebida con índices avanzados
* **Pytest** — Suite de pruebas unitarias (13 casos de prueba)
* **Ruff + Black** — Linting y formateo de código
* **Git Submodules** — Gestión de la dependencia de archivos GeoJSON

---

## 📡 Fuentes de Datos

1. **Catálogo Nacional de Códigos Postales:** Proporcionado por SEPOMEX (Correos de México) en formato de datos abiertos — [cpdescarga.txt](https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt).
2. **Límites Geográficos (GeoJSON):** Repositorio de la comunidad [Open Mexico GeoJSON](https://github.com/open-mexico/mexico-geojson) — polígonos de colonias para los 32 estados.

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio y los submódulos

Los mapas GeoJSON están enlazados como submódulo Git:

```bash
git clone --recurse-submodules https://github.com/open-mexico/sepomex-db-generator
cd sepomex-db-generator
```

### 2. Instalar dependencias

Se recomienda usar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generar las Bases de Datos

```bash
python src/main.py
```

Al finalizar, se generan los siguientes archivos en `dist/`:

| Archivo | Tamaño aprox. | Uso recomendado |
|---|---|---|
| `dist/db_postal.sqlite` | ~15 MB | Autocompletado de CPs, validación postal, búsquedas por nombre/estado |
| `dist/db_geo.sqlite` | ~350 MB | Geocodificación inversa, renderizado de mapas, análisis espacial |
| `dist/db_geo_errores.log` | Variable | Auditoría: CPs sin polígono GeoJSON asignado |

---

## 🔍 Consultas de Ejemplo

```sql
-- Buscar colonias por código postal
SELECT nombre, tipo, ciudad FROM colonias WHERE codigo = '06600';

-- Autocompletado de colonias por nombre (case-insensitive)
SELECT codigo, nombre, ciudad FROM colonias
WHERE nombre LIKE 'Roma%' AND estado_id = '09'
LIMIT 10;

-- Geocodificación inversa por coordenadas (bounding box)
SELECT codigo, nombre, ciudad FROM colonias
WHERE min_lat <= 19.4326 AND max_lat >= 19.4326
  AND min_lon <= -99.1332 AND max_lon >= -99.1332;

-- Colonias cercanas por centroide (nearest neighbor aproximado)
SELECT codigo, nombre,
       ABS(centro_lat - 19.4326) + ABS(centro_lon - (-99.1332)) AS distancia
FROM colonias
ORDER BY distancia ASC
LIMIT 5;
```

---

## 🧪 Pruebas Unitarias

El proyecto cuenta con una suite de 13 pruebas que cubre normalización de datos, creación de índices, inyección de geometría, manejo de duplicados, normalización de texto y generación del log de auditoría — sin necesidad de conexión a internet.

```bash
pytest -v
```

---

## 🎨 Formato y Lint

```bash
# Verificar estilo
ruff check .
black --check .

# Autoformatear
black .
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Áreas de interés:

* Soporte para formatos adicionales (Shapefile SHP, KML, GeoPackage)
* Relaciones formales (FK/PK) en el esquema SQLite
* Exportación a PostGIS o DuckDB para análisis geoespacial avanzado
* Mejoras al algoritmo de resolución de polígonos duplicados

Haz un fork y envía un pull request.

---

## 📄 Licencia

Este proyecto está bajo la **Licencia BSD 3-Clause**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

> Los datos originales de SEPOMEX están sujetos a los términos de libre uso de datos abiertos del Gobierno de México.

---

## 🔍 Palabras Clave

códigos postales México · SEPOMEX base de datos SQLite · GeoJSON colonias México · geocodificación inversa México · base de datos postal México · polígonos códigos postales · ETL Python SEPOMEX · SQLite geoespacial México · bounding box colonias · centroides códigos postales · Correos de México SQL · open data México · asentamientos humanos México · municipios estados México SQLite

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/macarthuror/