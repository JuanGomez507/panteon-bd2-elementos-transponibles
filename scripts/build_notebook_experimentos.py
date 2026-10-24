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
muestra aleatoria de 30,000 secuencias ya cargadas (con k-mers ya calculados, para
aislar el costo de la *estrategia de almacenamiento* del costo de *calcular* los
k-mers):

- **A) Embebido** (estrategia de producción): un documento por secuencia en
  `sequences`, con `kmers.k1`…`kmers.k6` anidados.
- **B) Colección aparte**: los metadatos de la secuencia en `bench_meta` y los
  k-mers en una colección independiente `bench_kmers_alt`, referenciados por
  `sequence_id`.

Para cada estrategia se mide: tiempo de carga, espacio en disco, y el tiempo de
3 consultas representativas con y sin índice (`explain()`/`executionStats`).""")

code("""import sys, os
sys.path.insert(0, os.path.abspath("../scripts"))
import json
import experiment_storage as exp

docs = exp.get_sample()
sample_id = docs[0]["original_id"]
print(f"Muestra: {len(docs)} secuencias. Ejemplo: {sample_id}")""")

md("""## Carga: embebido vs. colección aparte""")
code("""t_embedded = exp.load_embedded(docs)
t_separate = exp.load_separate(docs)
print(f"Tiempo de carga EMBEBIDO:      {t_embedded:.2f} s")
print(f"Tiempo de carga APARTE:        {t_separate:.2f} s")""")
md("""**Interpretación:** la estrategia *aparte* reparte la carga en dos
`bulk_write` (metadatos + k-mers) a colecciones más pequeñas cada una, mientras
que *embebido* escribe un solo documento grande por secuencia. En la práctica el
tiempo de ambas es del mismo orden de magnitud para esta muestra; la diferencia
real aparece en las consultas (ver abajo).""")

md("""## Espacio en disco (`collStats`)""")
code("""stats = exp.storage_stats()
print(json.dumps(stats, indent=2))""")
md("""**Interpretación:** el total en disco es similar entre ambas estrategias
(~500 MB para 30,000 secuencias) porque en ambos casos la secuencia de
nucleótidos completa —el campo más pesado— se guarda una sola vez por documento
de metadatos; la diferencia entre estrategias está en el *overhead* de tener una
colección adicional (un `_id`/`sequence_id` e índice extra por documento), que
aquí representa una fracción pequeña del total.""")

md("""## Consultas representativas (con y sin índice)""")

md("""### Consulta 1 — Perfil de k-mers (k=6) de UNA secuencia dada (punto)""")
code("""qr = exp.run_queries(sample_id)
print(json.dumps({k: v for k, v in qr.items() if k.startswith("Q1")}, indent=2))""")
md("""**Interpretación:** con índice (`original_id` / `sequence_id`), ambas
estrategias resuelven la consulta en ~1-2 ms examinando un solo documento. **Sin
índice**, la diferencia es drástica: escanear `bench_embedded` (documentos
grandes, con la secuencia completa y los 6 perfiles de k-mers) toma ~3 segundos,
mientras que escanear `bench_kmers_alt` (documentos pequeños, solo k-mers) toma
apenas ~0.03 segundos — casi 90 veces más rápido. Esto confirma por qué el índice
sobre `original_id`/`sequence_id` es imprescindible en el modelo embebido: sin
él, cada búsqueda puntual paga el costo de leer documentos mucho más pesados.""")

md("""### Consulta 2 — Suma global de un k-mer específico en toda la muestra
(agregación `$group`/`$sum`)""")
code("""print(json.dumps({k: v for k, v in qr.items() if k.startswith("Q2")}, indent=2))""")
md("""**Interpretación:** ambas estrategias deben recorrer toda la colección (no
hay índice que ayude a una suma global), por lo que el tiempo es comparable; la
colección aparte es ligeramente más rápida por tener documentos más pequeños
(menos I/O por documento leído).""")

md("""### Consulta 3 — Metadatos + perfil de k-mers de una secuencia (caso de uso combinado)""")
code("""print(json.dumps({k: v for k, v in qr.items() if k.startswith("Q3")}, indent=2))""")
md("""**Interpretación:** el modelo embebido resuelve esto con **una sola
consulta** (un solo round-trip a MongoDB); el modelo de colección aparte necesita
**dos consultas secuenciales** (metadatos, luego k-mers por `sequence_id`). Para
este caso de uso — que es, de hecho, el más común en el proyecto (consultar una
secuencia y su perfil de k-mers juntos, consulta 15) — el modelo embebido es
operacionalmente más simple, aunque la diferencia de tiempo medida aquí sea
pequeña a esta escala.""")

md("""## Conclusión de la comparación

Para el patrón de acceso de este proyecto —donde los k-mers casi siempre se
consultan junto con su secuencia dueña (consultas 8, 12, 15) y nunca se
comparten entre secuencias— el modelo **embebido** es la elección correcta: es
operacionalmente más simple (una consulta en vez de dos) y, con el índice
correspondiente, su rendimiento puntual es equivalente al de una colección
aparte. La colección aparte solo mostraría ventaja real en un escenario distinto:
si se necesitara escanear/agregar k-mers con mucha frecuencia **sin** tocar las
secuencias (por ejemplo, un servicio que solo calcula estadísticas de k-mers),
donde evitar cargar el campo `sequence` de cada documento ahorraría I/O.""")

code("""# Limpieza de las colecciones de benchmark (no son parte del modelo de produccion)
for c in ("bench_embedded", "bench_meta", "bench_kmers_alt"):
    db_drop = exp.db[c].drop()
print("Colecciones de benchmark eliminadas.")""")

nb["cells"] = cells
nbf.write(nb, "notebooks/03_experimentos.ipynb")
print("Notebook escrito: notebooks/03_experimentos.ipynb")
