"""Genera notebooks/01_pipeline_extraccion.ipynb: lectura/limpieza de FASTA y CSV,
cruce de fuentes, cálculo de k-mers y carga en MongoDB (demostrado con una
muestra; la carga completa de 239,946 secuencias se ejecuta con
`python scripts/load_sequences.py`, ver README.md)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# Pipeline de extracción — PanTEon en MongoDB

Bases de Datos II · Proyecto del segundo corte

Este notebook documenta, paso a paso, el pipeline de limpieza y carga implementado
en `scripts/`: lectura y limpieza del CSV, lectura y validación del FASTA, cruce
de ambas fuentes, cálculo de k-mers (k=1–6) y dos atributos adicionales, y carga
en MongoDB con inserciones masivas.

Por el tamaño del FASTA (~990 MB, 239,946 secuencias) y el costo de calcular
k-mers de k=1 a 6 para cada una (~30 minutos), este notebook **demuestra el
pipeline completo sobre una muestra pequeña**, siguiendo la recomendación del
enunciado de "probar primero con pocas especies y escalar cuando el pipeline
funcione". La carga de producción (las 239,946 secuencias ya cargadas en la base
`panteon` que usan `02_consultas.ipynb` y `03_experimentos.ipynb`) se ejecutó con:

```bash
python scripts/setup_db.py
python scripts/load_species.py
python scripts/load_sequences.py   # sin --limit: las 239,946 secuencias completas
```""")

code("""import sys, os
sys.path.insert(0, os.path.abspath("../scripts"))
import pandas as pd
from pymongo import MongoClient""")

# --------------------------------------------------------------------------
md("""## 1. Limpieza del CSV de metadatos

Se conservan solo las 9 columnas requeridas (sección 3.2 del enunciado), se
normalizan espacios/mayúsculas y se detectan valores "faltantes" disfrazados de
texto (p. ej. `"No trobat"`, `"Not order identified..."`) — ver
`docs/data_quality_notes.md` para el detalle completo del hallazgo.""")
code("""from clean_csv import load_clean_csv

df = load_clean_csv("../PanTEon_Database_metadata_v1.6.1.csv")
print("Filas:", len(df), " Columnas:", list(df.columns))
df.head(3)""")
code("""print("Nulos por columna tras la limpieza:")
print(df.isna().sum())""")

# --------------------------------------------------------------------------
md("""## 2. Lectura y validación del FASTA (streaming)

El archivo (~990 MB) se recorre línea por línea, sin cargarlo completo en
memoria. Se valida el formato del encabezado, se detectan IDs duplicados y se
revisa el alfabeto de nucleótidos usado.""")
code("""import re
from itertools import islice

HEADER_RE = re.compile(r"^>(\\S+)#([^/]+)/([^/]+)/([^@]+)\\s*@(.+)$")

def fasta_records(path, limit=None):
    header, chunks, n = None, [], 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\\n")
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(chunks)
                    n += 1
                    if limit is not None and n >= limit:
                        return
                header, chunks = line, []
            else:
                chunks.append(line)
        if header is not None:
            yield header, "".join(chunks)

# Muestra de las primeras 300 secuencias del archivo, para la demostración del pipeline.
sample = list(fasta_records("../PanTEon_Database_v1.6.1.fasta", limit=300))
print("Registros en la muestra:", len(sample))

bad_headers = [h for h, s in sample if not HEADER_RE.match(h)]
print("Encabezados invalidos en la muestra:", len(bad_headers))""")

# --------------------------------------------------------------------------
md("""## 3. Cruce FASTA ↔ CSV por especie

Se normaliza el nombre de especie (minúsculas, sin puntos) para resolver el caso
de `subsp.`/`sp.` con y sin punto encontrado en la exploración inicial, y se
reportan las especies de cada lado que no logran cruzar.

A diferencia del resto del notebook, este paso se hace sobre el **FASTA
completo**: solo se leen los encabezados (no las secuencias ni los k-mers), así
que recorrer las 239,946 entradas toma segundos. Se compara en ambas
direcciones (FASTA → CSV y CSV → FASTA), primero con los nombres tal como
vienen y luego con la llave normalizada.""")
code("""from clean_csv import species_match_key

# Especies de TODO el FASTA, leyendo solo las líneas de encabezado.
fasta_species_raw = set()
n_headers = 0
with open("../PanTEon_Database_v1.6.1.fasta", "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        if line.startswith(">"):
            n_headers += 1
            m = HEADER_RE.match(line.rstrip())
            if m:
                fasta_species_raw.add(m.group(5).strip())

csv_species_raw = set(df["species"])
print("Encabezados leídos:", n_headers)
print("Especies distintas -> FASTA:", len(fasta_species_raw), " CSV:", len(csv_species_raw))

print()
print("Sin normalizar:")
print("  En el FASTA pero no en el CSV:", sorted(fasta_species_raw - csv_species_raw))
print("  En el CSV pero no en el FASTA:", sorted(csv_species_raw - fasta_species_raw))

fasta_keys = {species_match_key(s) for s in fasta_species_raw}
csv_keys = set(df["match_key"])
print()
print("Con la llave normalizada (minúsculas, sin puntos):")
print("  En el FASTA pero no en el CSV:", sorted(fasta_keys - csv_keys))
print("  En el CSV pero no en el FASTA:", sorted(csv_keys - fasta_keys))""")
md("""**Resultado:** sin normalizar, 4 especies no cruzan en cada dirección, y son
las mismas en ambos lados escritas con y sin punto (`subsp.`/`subsp`,
`sp.`/`sp`). Con la llave normalizada, las 2790 especies cruzan en ambas
direcciones y no queda ninguna huérfana. Por eso la carga
(`load_sequences.py`) busca la especie por `match_key` y no por el nombre
original.""")

# --------------------------------------------------------------------------
md("""## 4. Cálculo de k-mers (k=1–6) y atributos adicionales

Los k-mers se calculan como **conteos dispersos** (solo las combinaciones
observadas, no un arreglo denso de 4^k posiciones) y se excluyen los k-mers que
contienen cualquier carácter distinto de A/C/G/T (ver `docs/data_model.md`,
sección de decisiones de diseño). Los atributos adicionales son `length`,
`gc_content` y `n_percentage`.""")
code("""from kmers import kmer_profiles, gc_content, n_percentage

header, seq = sample[0]
seq = seq.upper()
print("Encabezado:", header)
print("Longitud:", len(seq), " GC%:", round(gc_content(seq), 2), " N%:", round(n_percentage(seq), 2))

profiles = kmer_profiles(seq)
print("k=1:", profiles["k1"])
print("k=2 (primeros 5):", dict(list(profiles["k2"].items())[:5]))
print("Numero de 6-mers distintos observados:", len(profiles["k6"]), "de 4096 posibles")""")

# --------------------------------------------------------------------------
md("""## 5. Esquema de MongoDB (colecciones, validación, índices)

Ver `scripts/setup_db.py` para el script completo. Crea `species` y `sequences`
con validación `$jsonSchema` (tipos, campos obligatorios, y un patrón
`^[ACGTN]+$` para `sequence`) y los índices descritos en `docs/data_model.md`.""")
code("""client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]
print("Colecciones existentes:", db.list_collection_names())
print("Especies cargadas (produccion):", db["species"].count_documents({}))
print("Secuencias cargadas (produccion):", db["sequences"].count_documents({}))""")

# --------------------------------------------------------------------------
md("""## 6. Carga con inserciones masivas (demostración con muestra)

Se usa `bulk_write` con `InsertOne` por lote (`BATCH_SIZE = 200` en
`scripts/load_sequences.py`), igual que en la carga de producción. Aquí se
demuestra sobre una colección de prueba (`sequences_demo`) con la muestra de 300
secuencias leída arriba, para no duplicar las 239,946 secuencias ya cargadas.""")
code("""from load_sequences import parse_header
from clean_csv import species_match_key
from pymongo import InsertOne

species_lookup = {d["match_key"]: d["_id"] for d in db["species"].find({}, {"match_key": 1})}
species_name_lookup = {d["_id"]: d["species_name"] for d in db["species"].find({}, {"species_name": 1})}

db["sequences_demo"].delete_many({})
ops = []
n_skipped = 0
for header, raw_seq in sample:
    parsed = parse_header(header)
    if parsed is None:
        continue
    seq_id, te_class, te_order, te_superfamily, especie = parsed
    species_id = species_lookup.get(species_match_key(especie))
    if species_id is None:
        n_skipped += 1
        continue
    seq = raw_seq.upper()
    doc = {
        "original_id": seq_id, "te_class": te_class, "te_order": te_order,
        "te_superfamily": te_superfamily, "species_id": species_id,
        "species_name": species_name_lookup[species_id], "sequence": seq,
        "length": len(seq), "gc_content": round(gc_content(seq), 4),
        "n_percentage": round(n_percentage(seq), 4), "kmers": kmer_profiles(seq),
    }
    ops.append(InsertOne(doc))

result = db["sequences_demo"].bulk_write(ops, ordered=False)
print(f"Insertados en sequences_demo: {result.inserted_count} (omitidos sin especie: {n_skipped})")

# limpieza: esta colección es solo para la demostración del pipeline
db["sequences_demo"].drop()
print("Coleccion de demostracion eliminada (la produccion vive en 'sequences').")""")

md("""**Reproducibilidad:** siguiendo el README, cualquier persona puede regenerar
la base completa desde cero ejecutando `setup_db.py`, `load_species.py` y
`load_sequences.py` sobre los dos archivos descargados de Zenodo.""")

nb["cells"] = cells
nbf.write(nb, "notebooks/01_pipeline_extraccion.ipynb")
print("Notebook escrito: notebooks/01_pipeline_extraccion.ipynb")
