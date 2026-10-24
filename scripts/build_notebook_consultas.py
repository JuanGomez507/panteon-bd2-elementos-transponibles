"""Genera notebooks/02_consultas.ipynb a partir de scripts/queries.py y
scripts/generate_libraries.py. Se ejecuta con nbconvert para dejar los
resultados ya calculados dentro del notebook."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


md("""# Consultas obligatorias — PanTEon en MongoDB

Bases de Datos II · Proyecto del segundo corte

Este notebook ejecuta las 15 consultas obligatorias de la sección 4.3 del enunciado,
la generación de bibliotecas FASTA (consultas 10 y 11) y dos preguntas de
investigación propias. Cada consulta muestra: la pregunta, el código (función de
`scripts/queries.py`), el resultado y su interpretación.""")

code("""import sys, os
sys.path.insert(0, os.path.abspath("../scripts"))
import json
import queries as q
import generate_libraries as lib

def show(data, limit=10):
    if isinstance(data, list):
        print(json.dumps(data[:limit], indent=2, default=str))
        if len(data) > limit:
            print(f"... ({len(data)} filas totales, se muestran {limit})")
    else:
        print(json.dumps(data, indent=2, default=str))""")

# --------------------------------------------------------------------------
md("## Cantidad de elementos")

md("""### Consulta 1
**¿Cuántos TEs hay por clase, por orden y por superfamilia en toda la base?**""")
code("""r1 = q.q1_count_by_classification()
print("--- Por clase ---"); show(r1["por_clase"])
print("--- Por orden ---"); show(r1["por_orden"])
print("--- Por superfamilia (top 10) ---"); show(r1["por_superfamilia"], 10)""")
md("""**Interpretación:** CLASSI (retrotransposones) domina ampliamente con 194,774
TEs (81.2%) frente a CLASSII (DNA transposones) con 45,172 (18.8%). Entre los
órdenes, LTR es el más abundante (119,368), seguido de LINE (68,382) y TIR
(36,471) — consistente con que LTR y LINE son retrotransposones, el mecanismo de
replicación "copiar y pegar" que tiende a generar más copias que los elementos de
clase II.""")

md("""### Consulta 2
**¿Cuántos TEs tiene cada especie, desglosados por clase, orden y superfamilia?**
(Ejemplo con una especie; la función acepta `species_name=None` para toda la base.)""")
code("""r2 = q.q2_count_by_species("Halicephalobus mephisto")
show(r2)""")
md("""**Interpretación:** *Halicephalobus mephisto* tiene solo 10 TEs en la base,
repartidos en 3 combinaciones clase/orden/superfamilia distintas — una biblioteca
pequeña, típica de las especies con pocos TEs anotados (ver consulta 4).""")

md("""### Consulta 3
**¿Cómo cambia la cantidad de TEs por clase y orden entre reinos? ¿Y entre phyla?**""")
code("""r3 = q.q3_counts_by_kingdom_and_phylum()
print("--- Por reino (primeras filas) ---"); show(r3["por_reino"], 10)""")
md("""**Interpretación:** en Animalia predomina LINE (44,477) sobre LTR (25,382);
en cambio Plantae y Fungi están dominados por LTR (ver consulta 1 y 6 para más
contexto) — refleja diferencias evolutivas conocidas en el "transposon landscape"
entre reinos: los retrotransposones LINE son más activos en genomas animales,
mientras que las plantas acumulan masivamente elementos LTR (particularmente
Gypsy y Copia).""")

md("""### Consulta 4
**¿Cuáles son las 10 especies con más TEs y las 10 con menos?**""")
code("""r4 = q.q4_top_bottom_species()
print("--- Top 10 ---"); show(r4["top"])
print("--- Bottom 10 ---"); show(r4["bottom"])""")
md("""**Interpretación:** *Malus domestica* (manzano) encabeza con 1627 TEs, seguida
de *Danio rerio* (pez cebra) con 1352. Las especies "bottom" tienen exactamente 1
TE cada una — probablemente genomas con bibliotecas de TEs apenas iniciadas o
especies con anotación preliminar, más que genomas realmente pobres en TEs.""")

# --------------------------------------------------------------------------
md("## Longitud y contenido GC")

md("""### Consulta 5
**¿Cuál es la longitud promedio, mínima y máxima de los TEs por clase, orden y
superfamilia?**""")
code("""r5 = q.q5_length_stats_by_classification()
print("--- Por clase ---"); show(r5["por_clase"])
print("--- Por orden ---"); show(r5["por_orden"])""")
md("""**Interpretación:** CLASSI es en promedio más del doble de largo que CLASSII
(4453 nt vs. 2137 nt) — coherente con que los retrotransposones LTR completos
incluyen genes de poliproteína (gag/pol) además de las repeticiones terminales,
mientras que muchos elementos de clase II son transposones más compactos.""")

md("""### Consulta 6
**¿Cuál es el porcentaje de GC promedio por orden y por reino?**""")
code("""r6 = q.q6_gc_by_order_and_kingdom()
print("--- Por orden ---"); show(r6["por_orden"])
print("--- Por reino ---"); show(r6["por_reino"])""")
md("""**Interpretación:** SINE y DIRS tienen el GC% más alto (~53%), mientras que
TIR y MAVERICK rondan el 40%. Entre reinos, Fungi tiene el GC% más alto (46.2%) y
Plantae el más bajo (41.2%), lo que es consistente con la composición de base
general de esos genomas (los genomas fúngicos suelen tener GC% más alto que los
de muchas plantas).""")

md("""### Consulta 7
**¿Qué TEs son los más largos y los más cortos de cada reino?**""")
code("""r7 = q.q7_longest_shortest_by_kingdom()
show(r7)""")
md("""**Interpretación:** los TEs más largos en los tres reinos son elementos LTR
(ERV o GYPSY) de 18,900–19,900 nt — cerca del máximo teórico observado en toda la
base (19,926 nt). Los más cortos rondan 81–100 nt, el límite inferior fijado por
la base de datos para considerar algo un TE.""")

# --------------------------------------------------------------------------
md("## Nombres y búsqueda de secuencias")

md("""### Consulta 8
**Buscar una secuencia por su nombre y mostrar su clasificación, especie y
taxonomía completa.**""")
code("""r8 = q.q8_search_by_id("PDB00000001")
show(r8)""")
md("""**Interpretación:** confirma el ejemplo del propio enunciado — `PDB00000001`
es un HELITRON de *Halicephalobus mephisto*, con taxonomía completa
Animalia/Nematoda/Chromadorea/Rhabditida/Panagrolaimidae recuperada vía
`$lookup`.""")

md("""### Consulta 9
**Listar los nombres de todas las secuencias de una superfamilia en una especie
dada.**""")
code("""r9 = q.q9_sequence_names_by_superfamily_species("HELITRON", "Halicephalobus mephisto")
show(r9)""")
md("""**Interpretación:** *Halicephalobus mephisto* tiene exactamente 2 TEs de la
superfamilia HELITRON en la base.""")

# --------------------------------------------------------------------------
md("""## Generación de bibliotecas

Construidas **a partir de una consulta a MongoDB** (no leyendo el FASTA original),
exportadas con el mismo formato de encabezado `>ID#CLASE/ORDEN/SUPERFAMILIA @Especie`.
Los archivos quedan en `data/libraries/`.""")

md("""### Consulta 10 — Biblioteca de una especie""")
code("""n = lib.library_by_species("Halicephalobus mephisto", "../data/libraries/Halicephalobus_mephisto.fasta")
print(f"{n} secuencias exportadas a data/libraries/Halicephalobus_mephisto.fasta")""")

md("""### Consulta 11 — Biblioteca de un reino""")
code("""n = lib.library_by_kingdom("Fungi", "../data/libraries/Fungi.fasta")
print(f"{n} secuencias exportadas a data/libraries/Fungi.fasta")""")
md("""**Interpretación:** ambas funciones reciben la especie o el reino como
parámetro (no están codificados a mano), por lo que la misma consulta genera la
biblioteca de cualquier especie o reino de la base.""")

# --------------------------------------------------------------------------
md("## Relaciones y calidad")

md("""### Consulta 12
**Consulta que use `$lookup` para unir secuencias con la taxonomía de su
especie.**""")
code("""r12 = q.q12_lookup_sequences_taxonomy(5)
show(r12)""")
md("""**Interpretación:** el `$lookup` resuelve correctamente la taxonomía (reino,
phylum) de cada secuencia a partir de su `species_id`, sin necesidad de duplicar
esos campos en cada uno de los 239,946 documentos de `sequences`.""")

md("""### Consulta 13
**Comparación por origen de los datos (columna `Source`).**""")
code("""r13 = q.q13_comparison_by_source()
show(r13)""")
md("""**Interpretación:** las bibliotecas `RM2+MCH` (generadas automáticamente)
cubren 2404 especies con 208,354 secuencias (86.7 secuencias/especie en
promedio), mientras que `Dfam` (base de referencia curada) cubre solo 386
especies pero con bibliotecas también sustanciales (81.8 secuencias/especie). La
diferencia más notable es la longitud promedio: 4375 nt en RM2+MCH vs. 1654 nt en
Dfam — probablemente porque Dfam incluye muchos fragmentos de consenso más cortos
y bibliotecas ancestrales de clado (ver `docs/data_quality_notes.md`).""")

md("""### Consulta 14
**Consulta de control de calidad propia: secuencias con porcentaje de N alto
(>5%, posible indicio de ensamblaje de baja calidad en esa región del genoma).**""")
code("""r14 = q.q14_quality_control()
show(r14)""")
md("""**Interpretación:** 4374 secuencias (1.82% del total) tienen más de 5% de
N's. Es una minoría, pero no despreciable — el pipeline las conserva (no las
descarta) y simplemente excluye los k-mers que contienen N, para no sesgar los
conteos.""")

# --------------------------------------------------------------------------
md("## K-mers")

md("""### Consulta 15
**Recuperar el perfil de k-mers de una secuencia dada, para un k dado.**""")
code("""r15 = q.q15_kmer_profile("PDB00000001", 2)
show(r15)""")
md("""**Interpretación:** el perfil de 2-mers de `PDB00000001` tiene las 16
combinaciones posibles presentes (secuencia larga y sin N), con AA (306) y TT
(234) como los más frecuentes — refleja el alto contenido de homopolímeros A/T
típico de regiones ricas en AT de este elemento.""")

# --------------------------------------------------------------------------
md("""## Preguntas propias""")

md("""### Propia 1
**¿Cuál es la superfamilia de TE más frecuente en cada reino?**""")
code("""p1 = q.p1_dominant_superfamily_per_kingdom()
show(p1)""")
md("""**Interpretación:** cada reino tiene una superfamilia dominante distinta —
ERV en Animalia, TAD1 en Fungi y COPIA en Plantae — lo que confirma que la
composición de TEs no es uniforme entre reinos y que agrupar por superfamilia
(no solo por clase/orden) aporta información filogenética relevante.""")

md("""### Propia 2
**¿Las superfamilias (agrupadas por orden) con más contenido GC tienden a tener
TEs más largos?**""")
code("""p2 = q.p2_gc_length_correlation_by_order()
show(p2, 11)""")
md("""**Interpretación:** no hay una relación clara: SINE tiene el GC% más alto
(53%) pero es de los órdenes más cortos (253 nt en promedio), mientras que LTR
tiene GC% intermedio (42.8%) pero es el más largo (5286 nt). El contenido GC y
la longitud de un TE parecen estar determinados por mecanismos biológicos
distintos (composición de base vs. estructura/mecanismo de transposición), no
correlacionados entre sí en esta base.""")

# --------------------------------------------------------------------------
md("""## Visualizaciones (sección 4.5)

Generadas con datos leídos desde MongoDB (resultado de agregaciones), no desde
el archivo original. Ver `scripts/visualizations.py` para el código completo;
las figuras quedan guardadas en `docs/article/figures/` para incluirse en el
artículo.""")

code("""import sys as _sys
_sys.path.insert(0, os.path.abspath("../scripts"))
import visualizations as viz
from IPython.display import Image, display

os.makedirs("../docs/article/figures", exist_ok=True)""")

md("""### Figura 1 — Composición de TEs por reino""")
code("""path = viz.fig1_composition_by_kingdom()
display(Image(filename=path))""")
md("""**Interpretación:** LTR domina en Plantae (~86,000) mientras que LINE domina
en Animalia (~44,500) — el mismo patrón ya observado en la consulta 3, ahora
visible de un vistazo para los 11 órdenes y los 3 reinos a la vez.""")

md("""### Figura 2 — Longitud de los TEs por orden (boxplot)""")
code("""path = viz.fig2_length_boxplot_by_order()
display(Image(filename=path))""")
md("""**Interpretación:** MAVERICK y LTR tienen las medianas de longitud más altas
y la dispersión más amplia; SINE y MITE son consistentemente cortos y con poca
dispersión — consistente con que SINE/MITE son elementos no autónomos muy
compactos, mientras que LTR/MAVERICK pueden incluir la maquinaria completa de
transposición.""")

md("""### Figura 3 — Contenido GC por reino""")
code("""path = viz.fig3_gc_by_kingdom()
display(Image(filename=path))""")
md("""**Interpretación:** Fungi tiene la mediana de GC% más alta y Plantae la más
baja, confirmando el patrón de la consulta 6; los rangos (P5–P95) se solapan
bastante entre los tres reinos, por lo que el GC% por sí solo no distingue
reinos de forma tajante a nivel de TE individual.""")

md("""### Figura 4 — Heatmap de 2-mers por orden""")
code("""path = viz.fig4_heatmap_dinucleotide_by_order()
display(Image(filename=path))""")
md("""**Interpretación:** casi todos los órdenes comparten el mismo patrón
dominante (AA/TT/AT altos, CG consistentemente el más bajo — el conocido
"CpG deficit" de los genomas eucariotas). RETROPOSON y SINE se distinguen del
resto por tener CC y GG relativamente más altos que los demás órdenes,
sugiriendo una composición de base ligeramente distinta en esas familias.""")

nb["cells"] = cells
nbf.write(nb, "notebooks/02_consultas.ipynb")
print("Notebook escrito: notebooks/02_consultas.ipynb")
