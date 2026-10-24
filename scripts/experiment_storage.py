"""Evaluación experimental (sección 4.4): compara dos estrategias de
almacenamiento de k-mers sobre la MISMA muestra de datos ya cargados en
`sequences` (no se recalculan k-mers, para aislar el costo de la estrategia de
almacenamiento del costo de cómputo):

  A) Embebido:      un documento por secuencia, con los k-mers anidados
                     (estrategia de producción, colección `sequences`).
  B) Colección aparte: metadatos de la secuencia en una colección y los
                     k-mers en otra, referenciados por `sequence_id`
                     (colecciones `bench_meta` / `bench_kmers_alt`).

Para cada estrategia se mide: tiempo de carga, espacio en disco
(`collStats`) y el tiempo de 3 consultas representativas con y sin índice,
usando `explain("executionStats")`.
"""
import time
from pymongo import MongoClient, InsertOne, ASCENDING

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]

SAMPLE_SIZE = 30000
BATCH = 500


def get_sample(n=SAMPLE_SIZE):
    return list(db["sequences"].aggregate([{"$sample": {"size": n}}]))


def load_embedded(docs):
    coll = db["bench_embedded"]
    coll.drop()
    t0 = time.time()
    batch = []
    for d in docs:
        doc = dict(d)
        doc.pop("_id", None)
        batch.append(InsertOne(doc))
        if len(batch) >= BATCH:
            coll.bulk_write(batch, ordered=False)
            batch = []
    if batch:
        coll.bulk_write(batch, ordered=False)
    elapsed = time.time() - t0
    coll.create_index([("original_id", ASCENDING)], name="idx_original_id")
    return elapsed


def load_separate(docs):
    meta_coll = db["bench_meta"]
    kmer_coll = db["bench_kmers_alt"]
    meta_coll.drop()
    kmer_coll.drop()

    t0 = time.time()
    meta_batch, kmer_batch = [], []
    for d in docs:
        seq_oid = d["_id"]
        meta = {k: v for k, v in d.items() if k not in ("kmers", "_id")}
        meta["_id"] = seq_oid
        meta_batch.append(InsertOne(meta))
        kmer_batch.append(InsertOne({"sequence_id": seq_oid, "kmers": d["kmers"]}))
        if len(meta_batch) >= BATCH:
            meta_coll.bulk_write(meta_batch, ordered=False)
            kmer_coll.bulk_write(kmer_batch, ordered=False)
            meta_batch, kmer_batch = [], []
    if meta_batch:
        meta_coll.bulk_write(meta_batch, ordered=False)
        kmer_coll.bulk_write(kmer_batch, ordered=False)
    elapsed = time.time() - t0

    meta_coll.create_index([("original_id", ASCENDING)], name="idx_original_id")
    kmer_coll.create_index([("sequence_id", ASCENDING)], name="idx_sequence_id")
    return elapsed


def storage_stats():
    emb = db.command("collstats", "bench_embedded")
    meta = db.command("collstats", "bench_meta")
    kmer = db.command("collstats", "bench_kmers_alt")
    return {
        "embebido_MB": round(emb["storageSize"] / 1e6, 2),
        "embebido_indices_MB": round(emb["totalIndexSize"] / 1e6, 2),
        "aparte_meta_MB": round(meta["storageSize"] / 1e6, 2),
        "aparte_kmers_MB": round(kmer["storageSize"] / 1e6, 2),
        "aparte_indices_MB": round((meta["totalIndexSize"] + kmer["totalIndexSize"]) / 1e6, 2),
        "aparte_total_MB": round((meta["storageSize"] + kmer["storageSize"]) / 1e6, 2),
    }


INDEX_NAME = {"bench_embedded": "idx_original_id", "bench_meta": "idx_original_id", "bench_kmers_alt": "idx_sequence_id"}


def _timed_explain(coll, filt_proj, use_index=True):
    coll_name = coll.name
    idx_name = INDEX_NAME[coll_name]
    if not use_index:
        db.command({"collMod": coll_name, "index": {"name": idx_name, "hidden": True}})
    filt, proj = filt_proj
    t0 = time.time()
    list(coll.find(filt, proj))
    elapsed = time.time() - t0
    explain = coll.find(filt, proj).explain()
    if not use_index:
        db.command({"collMod": coll_name, "index": {"name": idx_name, "hidden": False}})
    exec_stats = explain.get("executionStats")
    return elapsed, exec_stats


def run_queries(sample_original_id, sample_k=6, sample_kmer="ATGCAT"):
    results = {}
    seq_oid = db["bench_meta"].find_one({"original_id": sample_original_id}, {"_id": 1})["_id"]

    # Consulta 1: punto - traer el perfil de k-mers de UNA secuencia dada.
    for use_index in (True, False):
        label = "con_indice" if use_index else "sin_indice"
        t, ex = _timed_explain(db["bench_embedded"], ({"original_id": sample_original_id}, {f"kmers.k{sample_k}": 1}), use_index=use_index)
        results.setdefault("Q1_perfil_kmers_embebido", {})[label] = {"tiempo_s": round(t, 5), "docsExamined": ex["totalDocsExamined"]}

        t, ex = _timed_explain(db["bench_kmers_alt"], ({"sequence_id": seq_oid}, {f"kmers.k{sample_k}": 1}), use_index=use_index)
        results.setdefault("Q1_perfil_kmers_aparte", {})[label] = {"tiempo_s": round(t, 5), "docsExamined": ex["totalDocsExamined"]}

    # Consulta 2: agregación - sumar el conteo de un k-mer especifico en toda la muestra.
    field = f"$kmers.k{sample_k}.{sample_kmer}"
    pipe = [{"$group": {"_id": None, "total": {"$sum": {"$ifNull": [field, 0]}}}}]
    t0 = time.time(); list(db["bench_embedded"].aggregate(pipe)); results["Q2_suma_global_kmer_embebido_s"] = round(time.time() - t0, 5)
    t0 = time.time(); list(db["bench_kmers_alt"].aggregate(pipe)); results["Q2_suma_global_kmer_aparte_s"] = round(time.time() - t0, 5)

    # Consulta 3: traer METADATOS + perfil de k-mers de una secuencia (caso de uso combinado).
    t0 = time.time()
    db["bench_embedded"].find_one({"original_id": sample_original_id})
    results["Q3_metadatos_y_kmers_embebido_s"] = round(time.time() - t0, 5)

    t0 = time.time()
    meta = db["bench_meta"].find_one({"original_id": sample_original_id})
    db["bench_kmers_alt"].find_one({"sequence_id": meta["_id"]})
    results["Q3_metadatos_y_kmers_aparte_s"] = round(time.time() - t0, 5)

    return results


if __name__ == "__main__":
    print(f"Tomando muestra de {SAMPLE_SIZE} secuencias desde 'sequences'...")
    docs = get_sample()
    sample_id = docs[0]["original_id"]

    t_emb = load_embedded(docs)
    t_sep = load_separate(docs)
    print(f"Tiempo de carga embebido: {t_emb:.2f} s")
    print(f"Tiempo de carga aparte:   {t_sep:.2f} s")

    stats = storage_stats()
    print("Almacenamiento:", stats)

    qr = run_queries(sample_id)
    import json
    print(json.dumps(qr, indent=2, default=str))
