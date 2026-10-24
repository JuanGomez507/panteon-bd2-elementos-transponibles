"""Exploración en streaming del FASTA de PanTEon (sin cargarlo completo en memoria)."""
import re
import time
from collections import Counter

FASTA_PATH = "PanTEon_Database_v1.6.1.fasta"
HEADER_RE = re.compile(r"^>(\S+)#([^/]+)/([^/]+)/([^@]+)\s*@(.+)$")

n_records = 0
n_bad_headers = 0
bad_header_examples = []
class_counter = Counter()
order_counter = Counter()
superfamily_counter = Counter()
species_counter = Counter()
char_counter = Counter()
lengths = []
ids_seen = set()
dup_ids = 0

t0 = time.time()
cur_len = 0
cur_chars = Counter()

with open(FASTA_PATH, "r", encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith(">"):
            if n_records > 0:
                lengths.append(cur_len)
                char_counter.update(cur_chars)
            n_records += 1
            cur_len = 0
            cur_chars = Counter()

            m = HEADER_RE.match(line)
            if not m:
                n_bad_headers += 1
                if len(bad_header_examples) < 10:
                    bad_header_examples.append(line)
                continue
            seq_id, clase, orden, superfam, especie = m.groups()
            especie = especie.strip()
            if seq_id in ids_seen:
                dup_ids += 1
            ids_seen.add(seq_id)
            class_counter[clase] += 1
            order_counter[orden] += 1
            superfamily_counter[superfam] += 1
            species_counter[especie] += 1
        else:
            cur_len += len(line)
            cur_chars.update(line)

# flush last record
if n_records > 0:
    lengths.append(cur_len)
    char_counter.update(cur_chars)

elapsed = time.time() - t0

print(f"Tiempo de lectura: {elapsed:.1f} s")
print(f"Total de registros: {n_records}")
print(f"Encabezados con formato inesperado: {n_bad_headers}")
print("Ejemplos de encabezados malos:", bad_header_examples)
print(f"IDs duplicados: {dup_ids}")
print()
print(f"Clases distintas: {len(class_counter)} -> {class_counter}")
print(f"Ordenes distintos: {len(order_counter)}")
print(f"Superfamilias distintas: {len(superfamily_counter)}")
print(f"Especies distintas en FASTA: {len(species_counter)}")
print()
print("--- Caracteres encontrados en secuencias (top 20) ---")
for ch, cnt in char_counter.most_common(20):
    print(repr(ch), cnt)
print()
import statistics
print("--- Longitudes ---")
print("min:", min(lengths), "max:", max(lengths), "media:", statistics.mean(lengths), "mediana:", statistics.median(lengths))
print()

# Guardar especies del FASTA para cruzar con el CSV
with open("scripts/_fasta_species.txt", "w", encoding="utf-8") as out:
    for sp in sorted(species_counter):
        out.write(sp + "\n")

print("Top 10 especies con más TEs:")
for sp, cnt in species_counter.most_common(10):
    print(" ", sp, cnt)
