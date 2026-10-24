# PanTEon-Mongo: Elementos Transponibles en MongoDB

Proyecto del segundo corte — Bases de Datos II (Universidad Autónoma de Manizales).
Diseño, implementación, población, consulta y evaluación de una base de datos en MongoDB
que integra secuencias de elementos transponibles (TEs), su taxonomía y sus perfiles de k-mers,
a partir de la base pública **PanTEon Database**.

## Estructura del repositorio

```
.
├── data/
│   ├── libraries/        # Bibliotecas .fasta generadas por consulta (especie / reino)
│   └── backup/           # Respaldo de MongoDB (mongodump) o script de regeneración
├── docs/
│   └── article/          # Artículo científico (.tex, .bib, figuras, PDF)
├── notebooks/            # Notebooks del pipeline y de consultas
├── scripts/              # Scripts reutilizables (carga, k-mers, utilidades)
├── JOURNAL.md             # Revista elegida y normas aplicadas
├── requirements.txt
└── README.md
```

## Datos

Este repositorio **no** incluye los archivos de datos crudos (son demasiado grandes para git).
Descárgalos de Zenodo y colócalos en la raíz del proyecto:

- Repositorio: https://zenodo.org/records/19372616
- `PanTEon_Database_v1.6.1.fasta` (~990 MB)
- `PanTEon_Database_metadata_v1.6.1.csv` (~370 kB)

## Instalación y ejecución desde cero

### Requisitos
- Python 3.11+ (probado con 3.14)
- MongoDB Community Server corriendo localmente (`localhost:27017`)

### 1. Clonar y crear el entorno

```bash
git clone <url-del-repo>
cd ProyectoCorte2
python -m venv .venv
.venv/Scripts/activate        # Windows
pip install -r requirements.txt
```

### 2. Descargar los datos

Descargar los dos archivos de Zenodo (ver sección Datos) y colocarlos en la raíz del proyecto.

### 3. Crear el esquema y cargar la base completa

```bash
python scripts/setup_db.py       # colecciones, $jsonSchema, índices
python scripts/load_species.py   # carga las 2790 especies del CSV
python scripts/load_sequences.py # carga las 239,946 secuencias (~30 min, calcula k-mers k=1-6)
```

`load_sequences.py` acepta `--limit N` para probar primero con una muestra pequeña
antes de lanzar la carga completa (recomendado).

`notebooks/01_pipeline_extraccion.ipynb` documenta el mismo pipeline paso a paso,
pero lo demuestra sobre una muestra pequeña (300 secuencias) por el costo de tiempo
de la carga completa — es material explicativo, no el método de carga de producción.

### 4. Ejecutar consultas, generar bibliotecas y figuras

```bash
jupyter notebook notebooks/02_consultas.ipynb
```

Resuelve las 15 consultas obligatorias + 2 propias, genera bibliotecas FASTA de
ejemplo (`data/libraries/`) y las 4 visualizaciones de la sección 4.5
(`docs/article/figures/`). Para generar todas las bibliotecas (las de reino son
pesadas, decenas-cientos de MB, y no se versionan en git):

```bash
python scripts/generate_libraries.py
```

### 5. Ejecutar la evaluación experimental

```bash
jupyter notebook notebooks/03_experimentos.ipynb
```

### 6. Compilar el artículo científico

```bash
tectonic docs/article/article.tex   # o pdflatex + bibtex, con texlive/miktex
```

## Citación de los datos

1. Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Goes F, Gaviria-Orrego S, Gómiz-Fernández J,
   Llatser-Torres J, Paschoal AR, Guyot R, Gabaldón T. (2026). *PanTEon: a cross-kingdom
   framework to guide the design of transposable element classifiers*. bioRxiv.
   https://doi.org/10.64898/2026.04.01.715927
2. PanTEon Database v1.6.1. Zenodo. https://zenodo.org/records/19372616

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
- [ ] **Pendiente: completar nombre(s) y correo de los autores en `docs/article/article.tex`**
      (quedó como placeholder `[Nombre completo del/los autor(es)]`) y recompilar
- [ ] Respaldo de la base de datos — se resuelve con el script de regeneración
      (`setup_db.py` + `load_species.py` + `load_sequences.py`); no se incluye un
      `mongodump` en el repo por su tamaño (~4 GB)
