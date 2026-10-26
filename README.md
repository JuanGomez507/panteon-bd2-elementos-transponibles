# PanTEon-Mongo: Elementos Transponibles en MongoDB

Proyecto del segundo corte — Bases de Datos II
(Universidad Autónoma de Manizales).

Diseño, implementación, población, consulta y evaluación
de una base de datos documental construida en MongoDB
que integra secuencias de elementos transponibles (TEs),
su taxonomía completa y sus perfiles de k-mers (k=1 a 6),
a partir de la base de datos pública PanTEon Database.

---

## Estructura detallada del repositorio

A continuación se describe la organización de carpetas
y archivos principales dentro del proyecto:

.
├── data/
│   ├── libraries/        # Bibliotecas .fasta generadas por consulta (especie / reino)
│   └── backup/           # Respaldo de MongoDB (mongodump) o script de regeneración
├── docs/
│   └── article/          # Artículo científico (.tex, .bib, figuras, PDF)
├── notebooks/            # Notebooks del pipeline y de consultas
├── scripts/              # Scripts reutilizables (carga, k-mers, utilidades)
├── JOURNAL.md             # Revista elegida y normas aplicadas
├── requirements.txt      # Librerías de Python requeridas
└── README.md             # Guía principal del proyecto

---

## Datos crudos y fuentes externas

Este repositorio no incluye los archivos de datos crudos
debido a que su peso excede los límites recomendados en Git.

Para replicar la base localmente, descarga los datos de Zenodo
y ubícalos directamente en la raíz del proyecto:

- Repositorio original de Zenodo:
  https://zenodo.org/records/19372616

- Archivo FASTA con las secuencias:
  PanTEon_Database_v1.6.1.fasta (~990 MB)

- Archivo CSV con los metadatos taxonómicos:
  PanTEon_Database_metadata_v1.6.1.csv (~370 kB)

---

## Instalación y ejecución paso a paso

### Requisitos previos del sistema

- Intérprete de Python 3.11+ (probado con Python 3.14).
- Servidor de MongoDB Community Server corriendo en local.
- Dirección por defecto: localhost:27017

---

### Step 1: Clonar el repositorio y preparar entorno virtual

Abre tu terminal de comandos e ingresa los siguientes pasos:

git clone <url-del-repo>
cd panteon-bd2-elementos-transponibles
python -m venv .venv
.venv/Scripts/activate        # Comando para Windows (PowerShell / CMD)
pip install -r requirements.txt

---

### Step 2: Descargar y posicionar los archivos de entrada

Descargar los dos archivos desde el enlace de Zenodo
y colocarlos en la carpeta raíz del proyecto:

1. PanTEon_Database_v1.6.1.fasta
2. PanTEon_Database_metadata_v1.6.1.csv

---

### Step 3: Inicializar esquemas y ejecutar la carga masiva

Para construir las colecciones en MongoDB, aplicar la validación
de esquemas mediante $jsonSchema e indexar los campos clave,
ejecuta los scripts en el siguiente orden:

python scripts/setup_db.py       # Crea colecciones, reglas $jsonSchema e índices
python scripts/load_species.py   # Procesa y carga las 2790 especies del CSV
python scripts/load_sequences.py # Carga las 239,946 secuencias y calcula k-mers (k=1-6)

**Nota de optimización:**
El script load_sequences.py acepta el argumento --limit N
para realizar pruebas con muestras reducidas antes de lanzar
la carga completa (la cual toma cerca de 30 minutos).

**Demostración paso a paso:**
El archivo notebooks/01_pipeline_extraccion.ipynb muestra
el funcionamiento del pipeline sobre una muestra de 300 registros
con fines meramente explicativos y pedagógicos.

---

### Step 4: Consultas analíticas, bibliotecas y visualizaciones

Abre el entorno interactivo de Jupyter Notebook:

jupyter notebook notebooks/02_consultas.ipynb

Este cuaderno resuelve las 15 consultas obligatorias del taller
más las 2 preguntas de investigación propias planteadas.

- Genera automáticamente las bibliotecas FASTA de muestra en:
  data/libraries/
- Construye las 4 figuras estadísticas ubicadas en:
  docs/article/figures/

Para generar todas las bibliotecas masivas de reinos:

python scripts/generate_libraries.py

---

### Step 5: Evaluación experimental de rendimiento

Para ejecutar la comparativa entre el modelo embebido
y la estrategia de colección separada sobre 30,000 registros:

jupyter notebook notebooks/03_experimentos.ipynb

---

### Step 6: Compilación del artículo científico

Para compilar el documento final en LaTeX:

tectonic docs/article/article.tex   # O mediante pdflatex + bibtex

---

## Citación oficial de los datos utilizados

1. Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Goes F, Gaviria-Orrego S, Gómiz-Fernández J, Llatser-Torres J, Paschoal AR, Guyot R, Gabaldón T. (2026). PanTEon: a cross-kingdom framework to guide the design of transposable element classifiers. bioRxiv.
   https://doi.org/10.64898/2026.04.01.715927

2. PanTEon Database v1.6.1. Zenodo.
   https://zenodo.org/records/19372616

## Estado del proyecto

- [x] Entorno configurado (MongoDB local + Python)
- [x] Exploración y limpieza de datos (`docs/data_quality_notes.md`)
- [x] Modelo de datos documental (`docs/data_model.md`)
- [x] Pipeline de carga (k-mers, atributos, inserciones masivas) — 239,946/239,946 cargadas
- [x] Consultas obligatorias (1–15) + 2 propias (`notebooks/02_consultas.ipynb`)
- [x] Bibliotecas FASTA generadas por consulta (especie y reino)
- [x] Evaluación experimental de estrategias de almacenamiento (`notebooks/03_experimentos.ipynb`)
- [x] Visualizaciones (4 figuras, `docs/article/figures/`)
- [x] Artículo científico (`docs/article/article.pdf` + fuentes `.tex`/`.bib`)
- [x] Autores y correos en el artículo
- [x] Respaldo de la base de datos — opción "script que la regenere"
      (`setup_db.py` + `load_species.py` + `load_sequences.py`); no se incluye un
      `mongodump` en el repo por su tamaño (~4 GB)
