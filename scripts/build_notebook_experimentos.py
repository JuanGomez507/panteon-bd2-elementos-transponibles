"""Genera notebooks/03_experimentos.ipynb: evaluación experimental de dos
estrategias de almacenamiento de k-mers (sección 4.4 del enunciado)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# Evaluación experimental — estrategias de almacenamiento de k-mers

Bases de Datos II · Proyecto del segundo corte

Compara dos estrategias de almacenamiento para los perfiles de k-mers, sobre una
muestra de 30,000 secuencias ya cargadas (con k-mers ya calculados, para aislar
el costo de la *estrategia de almacenamiento* del costo de *calcular* los
k-mers). La muestra es **reproducible**: se eligen los identificadores con una
semilla fija (`SEED = 42`), así que cada ejecución usa las mismas secuencias.

- **A) Embebido** (estrategia de producción): un documento por secuencia, con
  `kmers.k1`…`kmers.k6` anidados (`bench_embedded`).
- **B) Colección aparte**: los metadatos de la secuencia en `bench_meta` y los
  k-mers en una colección independiente `bench_kmers_alt`, referenciados por
  `sequence_id`.

Para cada estrategia se mide:

1. tiempo de carga (`bulk_write`);
2. espacio en disco (`collStats`);
3. tres consultas representativas **con y sin índice**, cada una analizada con
   `explain` en verbosidad `"executionStats"`.

Para la versión *sin índice* los índices secundarios se **ocultan**
(`collMod` con `hidden: true`) en lugar de borrarse: el planificador deja de
usarlos y la consulta cae en un `COLLSCAN`, pero no hay que reconstruirlos
después. Cada medición se repite 3 veces y se reporta la mediana.""")

code("""import sys, os
sys.path.insert(0, os.path.abspath("../scripts"))
import json
import pandas as pd
import experiment_storage as exp

docs = exp.get_sample()
print(f"Muestra: {len(docs)} secuencias (semilla {exp.SEED})")""")

md("""## Carga: embebido vs. colección aparte""")
code("""t_embedded = exp.load_embedded(docs)
t_separate = exp.load_separate(docs)
print(f"Tiempo de carga EMBEBIDO: {t_embedded:.2f} s")
print(f"Tiempo de carga APARTE:   {t_separate:.2f} s")""")
md("""**Interpretación:** la colección aparte hace el doble de `bulk_write`
(metadatos + k-mers) y mantiene un índice adicional sobre `sequence_id`, por
lo que su carga es algo más lenta que la embebida. Ambas están en el mismo
orden de magnitud: el costo dominante del pipeline real no es la escritura sino
el cálculo de los k-mers, que aquí se excluyó a propósito.""")

md("""## Espacio en disco (`collStats`)""")
code("""stats = exp.storage_stats()
print(json.dumps(stats, indent=2))""")
md("""**Interpretación:** `storageSize` es el espacio real en disco, ya
comprimido por WiredTiger; `size` (tamaño lógico) es el BSON sin comprimir.
El tamaño lógico de ambas estrategias es casi el mismo —los datos son los
mismos, la colección aparte solo añade un `_id` y un `sequence_id` por
documento—, así que cualquier diferencia en `storageSize` se debe a cómo
comprime WiredTiger cada colección y no a que una estrategia guarde menos
información. Separar los k-mers deja documentos más homogéneos en cada
colección, lo que tiende a comprimir mejor. Hay que leer este resultado con
cautela: `storageSize` también incluye espacio reservado por el motor que
varía de una ejecución a otra.""")

md("""## Consultas representativas (con y sin índice)

| # | Consulta | Embebido | Colección aparte |
|---|---|---|---|
| Q1 | Perfil de k-mers (k=6) de **una** secuencia, por `original_id` | 1 `find` | `find` en `bench_meta` → `find` en `bench_kmers_alt` |
| Q2 | Perfiles de k-mers de **todas** las secuencias de una especie (la de más secuencias en la muestra), por `species_id` | 1 `find` | `find` en `bench_meta` → `find` con `$in` en `bench_kmers_alt` |
| Q3 | Metadatos + perfil de k-mers completo de una secuencia | 1 `find` | 2 `find` |

Q1 y Q3 representan el acceso puntual (consultas 8 y 15 del enunciado); Q2
representa un acceso por rango (consultas 9 y 10).""")
code("""sample_id, species_id, species_name, n_species = exp.pick_query_targets()
print(f"Secuencia de ejemplo: {sample_id}")
print(f"Especie para Q2: {species_name} ({n_species} secuencias en la muestra)")

qr = exp.run_queries(sample_id, species_id)
table = pd.DataFrame(exp.results_table(qr))
table""")

md("""### Resumen: ¿cuánto ayuda el índice?""")
code("""pivot = table.pivot_table(index=["consulta", "estrategia"], columns="indice",
                          values=["tiempo_cliente_ms", "docsExamined"])
pivot""")
md("""**Interpretación:**

- **Con índice**, las tres consultas usan `IXSCAN` y examinan exactamente los
  documentos que devuelven (1 en Q1/Q3, los de la especie en Q2; el doble en la
  colección aparte, porque cada secuencia ocupa dos documentos). Su tiempo en el
  servidor es de 0–1 ms en ambas estrategias.
- **Sin índice**, todas caen en `COLLSCAN` y examinan la colección completa
  (30,000 documentos en el embebido y 60,000 en la colección aparte, que recorre
  dos colecciones). En Q1 y Q3 el tiempo pasa de menos de 1 ms a varias
  decenas de milisegundos; en Q2 el tiempo en el servidor también se multiplica
  por más de 20.
- La colección aparte siempre necesita **dos consultas** donde la embebida usa
  una. Con índice el segundo paso cuesta poco, pero sin índice paga dos
  recorridos completos y es la más lenta de las dos.
- En Q2 el tiempo del cliente es mucho mayor que el del servidor también con
  índice: la consulta devuelve cientos de perfiles de 6-mers y casi todo el
  costo está en transferirlos y decodificarlos, no en encontrarlos.

El índice importa más que la estrategia de almacenamiento: con índice ambas
estrategias quedan en el orden del milisegundo, y sin él ambas recorren toda
la colección.""")

md("""### Referencia: agregación global (Q4)

Suma del conteo de un 6-mer en toda la muestra. Ningún índice puede acelerarla
(tiene que leer todos los documentos), así que se mide una sola vez por
estrategia.""")
code("""print(json.dumps(qr["Q4_suma_global_kmer_(referencia)"], indent=2))""")
md("""**Interpretación:** ambas estrategias leen los 30,000 documentos. Los
documentos de `bench_kmers_alt` no incluyen la secuencia ni los metadatos,
pero los perfiles de k-mers dominan el tamaño de cada documento, así que la
ventaja de la colección aparte es pequeña.""")

md("""## Conclusión de la comparación

Para el patrón de acceso de este proyecto —donde los k-mers casi siempre se
consultan junto con su secuencia (consultas 8, 12, 15) y nunca se comparten
entre secuencias— el modelo **embebido** es la elección correcta: resuelve cada
caso con una sola consulta y, con los índices adecuados, su tiempo es
equivalente al de la colección aparte. La colección aparte ahorra espacio en
disco por compresión y podría convenir en otro escenario: un servicio que
agrega k-mers con mucha frecuencia sin necesitar nunca la secuencia ni sus
metadatos.""")

code("""# Limpieza de las colecciones de benchmark (no son parte del modelo de produccion)
exp.drop_bench_collections()
print("Colecciones de benchmark eliminadas.")""")

nb["cells"] = cells
nbf.write(nb, "notebooks/03_experimentos.ipynb")
print("Notebook escrito: notebooks/03_experimentos.ipynb")
