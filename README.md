# 🇲🇽 MexPost Data: Generador de Base de Datos de Códigos Postales y GeoJSON de México

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Optimized-lightgrey.svg)](https://www.sqlite.org/)
[![License: BSD 3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Generador automatizado (ETL) para descargar, limpiar y cruzar el catálogo oficial de Códigos Postales de Correos de México (SEPOMEX) con polígonos geoespaciales (GeoJSON). Genera bases de datos SQLite listas para producción y altamente optimizadas.

---

## 🌍 Abstract (English)
`sepomex-db-generator` is an open-source ETL (Extract, Transform, Load) pipeline designed to democratize and simplify access to geographic and postal data in Mexico. By downloading the official raw catalog from SEPOMEX and combining it with local GeoJSON boundary files, this tool generates lightweight, relational, and highly indexed SQLite databases. It bridges the gap between messy government text files and modern, high-performance microservices, providing developers with ready-to-use spatial data for mapping, geocoding, and logistics applications.

## 📄 Resumen (Español)
`sepomex-db-generator` es un pipeline ETL de código abierto diseñado para democratizar y simplificar el acceso a datos postales y geográficos en México. Extrae el catálogo oficial crudo de SEPOMEX, lo normaliza estructuralmente y lo cruza con polígonos GeoJSON. El resultado son bases de datos SQLite relacionales, ligeras y pre-indexadas, cerrando la brecha entre archivos gubernamentales de texto plano y el desarrollo de microservicios modernos o sistemas de información geográfica (SIG).

---

## 🎯 Objetivo
El objetivo principal de este proyecto es proporcionar una fuente de verdad **reproducible** y **agnóstica** sobre la división postal de México. En lugar de compartir bases de datos desactualizadas, este repositorio proporciona el *motor* para construir tu propia base de datos actualizada en segundos, normalizando la información en un formato relacional ideal para desarrolladores backend y científicos de datos.

## ✨ Características Principales

* **Extracción Automatizada:** Descarga directa del archivo oficial más reciente de Correos de México.
* **Normalización Relacional:** Divide los datos planos en 3 tablas optimizadas: `estados`, `municipios` y `colonias`.
* **Inyección Espacial:** Vincula automáticamente límites geográficos (polígonos GeoJSON) a cada código postal.
* **Índices de Alto Rendimiento:** Pre-configuración de índices en SQLite (con `COLLATE NOCASE`) garantizando búsquedas en milisegundos para coincidencias exactas o parciales (`LIKE`), incluso con millones de registros.
* **Arquitectura Limpia y Segura:** Código modularizado respaldado por pruebas unitarias automatizadas (`pytest`).
* **Bases de Datos Dual:** Genera una versión ligera (solo texto) y una versión espacial (con geometría JSON) según las necesidades de tu proyecto.

## 🛠️ Tecnologías

* **Python 3** (Lenguaje principal del script ETL)
* **Pandas** (Limpieza, transformación y manipulación masiva de datos)
* **SQLite3** (Motor de base de datos embebida y relacional)
* **Pytest** (Entorno de pruebas unitarias y validación)
* **Git Submodules** (Gestión de la dependencia de archivos GeoJSON)

## 📡 Fuentes de Datos

1. **Catálogo Nacional de Códigos Postales:** Proporcionado por SEPOMEX (Correos de México) en formato de datos abiertos.
2. **Límites Geográficos (GeoJSON):** Repositorio de la comunidad [Open Mexico GeoJSON](https://github.com/open-mexico/mexico-geojson).

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio y los submódulos
Debido a que los mapas están enlazados mediante submódulos, clona el proyecto con el siguiente comando:
```bash
git clone --recurse-submodules https://github.com/open-mexico/sepomex-db-generator
cd sepomex-db-generator
```

2. Instalar dependencias
Es recomendable usar un entorno virtual (venv).

```bash
pip install -r requirements.txt
```

3. Generar las Bases de Datos
Ejecuta el orquestador principal. Este proceso descargará la información, aplicará la limpieza y cruzará los datos con los archivos GeoJSON locales.

```bash
python src/main.py
```

Al finalizar, obtendrás dos archivos en la raíz de tu proyecto:

`db_postal.sqlite` (Solo texto, ideal para autocompletados web rápidos).

`db_geo.sqlite` (Texto + Polígonos GeoJSON, ideal para geocodificación inversa o renderizado de mapas).

## 🧪 Pruebas Unitarias (Testing)
El código cuenta con cobertura para asegurar que la normalización de datos funciona correctamente sin necesidad de consumir el servicio en línea.

Para ejecutar las pruebas:

```bash
pytest -v
```

## 🎨 Formato y Lint
El proyecto valida estilo y calidad de código con `black` y `ruff`.

Para ejecutar las validaciones localmente:

```bash
ruff check .
black --check .
```

Si deseas autoformatear el código:

```bash
black .
```

## 🔍 Palabras Clave
- Códigos postales México
- SEPOMEX base de datos
- GeoJSON México
- SQLite México
- Base de datos códigos postales
- Polígonos de colonias
- ETL Python
- Geocodificación México
- Open Data Mexico
- Correos de México SQL

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si deseas agregar soporte para nuevos formatos geográficos (como SHP o KML) o mejorar los algoritmos de limpieza, siéntete libre de hacer un fork y enviar un pull request.

📄 Licencia
Este proyecto está bajo la Licencia BSD 3-Clause. Consulta el archivo LICENSE para más detalles. (Nota: Los datos originales de SEPOMEX están sujetos a los términos de libre uso de datos abiertos del Gobierno de México).