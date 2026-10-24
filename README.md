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
├── JOURNAL.md             # Revista elegida y normas aplicadas (pendiente)
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

### 3. Ejecutar el pipeline

```bash
jupyter notebook notebooks/01_pipeline_extraccion.ipynb
```

Esto lee y limpia el FASTA y el CSV, cruza ambas fuentes, calcula los perfiles de k-mers
(k=1 a 6) y dos atributos adicionales por secuencia, y carga todo en MongoDB mediante
inserciones masivas (`insert_many` / `bulk_write`).

### 4. Ejecutar consultas y generar bibliotecas / figuras

```bash
jupyter notebook notebooks/02_consultas.ipynb
```

### 5. Ejecutar la evaluación experimental

```bash
jupyter notebook notebooks/03_experimentos.ipynb
```

## Citación de los datos

1. Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Goes F, Gaviria-Orrego S, Gómiz-Fernández J,
   Llatser-Torres J, Paschoal AR, Guyot R, Gabaldón T. (2026). *PanTEon: a cross-kingdom
   framework to guide the design of transposable element classifiers*. bioRxiv.
   https://doi.org/10.64898/2026.04.01.715927
2. PanTEon Database v1.6.1. Zenodo. https://zenodo.org/records/19372616

## Estado del proyecto

- [x] Entorno configurado (MongoDB local + Python)
- [ ] Exploración y limpieza de datos
- [ ] Modelo de datos documental
- [ ] Pipeline de carga (k-mers, atributos, inserciones masivas)
- [ ] Consultas obligatorias (1–15) + 2 propias
- [ ] Evaluación experimental de estrategias de almacenamiento
- [ ] Visualizaciones
- [ ] Artículo científico
