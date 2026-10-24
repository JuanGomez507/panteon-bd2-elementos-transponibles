"""Pipeline de carga de secuencias: lee el FASTA en streaming, cruza con species,
calcula atributos y perfiles de k-mers, y carga en MongoDB con bulk_write.

Uso:
    python load_sequences.py --limit 500      # prueba rápida con una muestra
    python load_sequences.py                  # carga completa (~240k secuencias)
"""
import argparse
import re
import time

from pymongo import MongoClient, InsertOne
from pymongo.errors import BulkWriteError

from kmers import kmer_profiles, gc_content, n_percentage
from clean_csv import species_match_key

HEADER_RE = re.compile(r"^>(\S+)#([^/]+)/([^/]+)/([^@]+)\s*@(.+)$")
BATCH_SIZE = 200

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]


def build_species_lookup():
    return {
        doc["match_key"]: doc["_id"]
        for doc in db["species"].find({}, {"match_key": 1})
    }


def build_species_name_lookup():
    return {
        doc["_id"]: doc["species_name"]
        for doc in db["species"].find({}, {"species_name": 1})
    }


def fasta_records(path):
    """Generador: produce (header_line, sequence_str) por registro, sin cargar todo el archivo."""
    header = None
    chunks = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith(">"):
                if header is not None:
                    yield header, "".join(chunks)
                header = line
                chunks = []
            else:
                chunks.append(line)
        if header is not None:
            yield header, "".join(chunks)


def parse_header(header):
    m = HEADER_RE.match(header)
    if not m:
        return None
    seq_id, te_class, te_order, te_superfamily, especie = m.groups()
    return seq_id, te_class, te_order, te_superfamily.strip(), especie.strip()


def run(fasta_path="PanTEon_Database_v1.6.1.fasta", limit=None):
    species_lookup = build_species_lookup()
    species_name_lookup = build_species_name_lookup()
    print(f"Especies en lookup: {len(species_lookup)}")

    n_processed = 0
    n_inserted = 0
    n_skipped_no_species = 0
    n_skipped_bad_header = 0
    skipped_species_examples = []

    batch = []
    t0 = time.time()

    for header, raw_seq in fasta_records(fasta_path):
        if limit is not None and n_processed >= limit:
            break
        n_processed += 1

        parsed = parse_header(header)
        if parsed is None:
            n_skipped_bad_header += 1
            continue
        seq_id, te_class, te_order, te_superfamily, especie = parsed

        key = species_match_key(especie)
        species_id = species_lookup.get(key)
        if species_id is None:
            n_skipped_no_species += 1
            if len(skipped_species_examples) < 10:
                skipped_species_examples.append(especie)
            continue

        seq = raw_seq.upper()
        doc = {
            "original_id": seq_id,
            "te_class": te_class,
            "te_order": te_order,
            "te_superfamily": te_superfamily,
            "species_id": species_id,
            "species_name": species_name_lookup[species_id],
            "sequence": seq,
            "length": len(seq),
            "gc_content": round(gc_content(seq), 4),
            "n_percentage": round(n_percentage(seq), 4),
            "kmers": kmer_profiles(seq),
        }
        batch.append(InsertOne(doc))

        if len(batch) >= BATCH_SIZE:
            n_inserted += _flush(batch)
            batch = []

    if batch:
        n_inserted += _flush(batch)

    elapsed = time.time() - t0
    print(f"Procesados: {n_processed}")
    print(f"Insertados: {n_inserted}")
    print(f"Sin especie en CSV (omitidos): {n_skipped_no_species} -> ejemplos: {skipped_species_examples}")
    print(f"Encabezado inválido (omitidos): {n_skipped_bad_header}")
    print(f"Tiempo: {elapsed:.1f} s")


def _flush(batch):
    try:
        result = db["sequences"].bulk_write(batch, ordered=False)
        return result.inserted_count
    except BulkWriteError as e:
        # Duplicados (original_id ya cargado) se ignoran; otros errores se muestran.
        write_errors = e.details.get("writeErrors", [])
        other = [we for we in write_errors if we.get("code") != 11000]
        if other:
            print("Errores no-duplicado:", other[:3])
        return e.details.get("nInserted", 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Número máximo de secuencias a procesar (prueba)")
    parser.add_argument("--fasta", type=str, default="PanTEon_Database_v1.6.1.fasta")
    args = parser.parse_args()
    run(fasta_path=args.fasta, limit=args.limit)
