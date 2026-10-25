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
(`collStats`) y tres consultas representativas con y sin índice, usando el
comando `explain` con verbosidad "executionStats" (tiempo de ejecución en el
servidor, documentos y llaves de índice examinados). Una cuarta consulta
(agregación global) se reporta aparte porque ningún índice la puede acelerar.

La muestra es reproducible: se eligen SAMPLE_SIZE identificadores con una
semilla fija, así que dos ejecuciones usan exactamente las mismas secuencias.
"""
import random
import statistics
import time

from pymongo import MongoClient, InsertOne, ASCENDING

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]

SAMPLE_SIZE = 30000
SEED = 42
BATCH = 500
REPEATS = 3  # repeticiones por medición; se reporta la mediana

BENCH_COLLECTIONS = ("bench_embedded", "bench_meta", "bench_kmers_alt")


def get_sample(n=SAMPLE_SIZE, seed=SEED):
    all_ids = sorted(d["original_id"] for d in db["sequences"].find({}, {"original_id": 1, "_id": 0}))
    chosen = random.Random(seed).sample(all_ids, n)
    return list(db["sequences"].find({"original_id": {"$in": chosen}}).sort("original_id", ASCENDING))


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
    coll.create_index([("species_id", ASCENDING)], name="idx_species_id")
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
    meta_coll.create_index([("species_id", ASCENDING)], name="idx_species_id")
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
        # Tamaño lógico (BSON sin comprimir), para separar el efecto de la
        # compresión de WiredTiger del tamaño real de los datos.
        "embebido_logico_MB": round(emb["size"] / 1e6, 2),
        "aparte_logico_MB": round((meta["size"] + kmer["size"]) / 1e6, 2),
    }


# ---------------------------------------------------------------------------
# Medición con explain("executionStats")
# ---------------------------------------------------------------------------

def _set_indexes_hidden(hidden):
    """Oculta (o vuelve a mostrar) todos los índices secundarios de las
    colecciones de benchmark. Un índice oculto no lo usa el planificador, así
    que la consulta se resuelve con un COLLSCAN, sin tener que borrarlo."""
    for name in BENCH_COLLECTIONS:
        for idx_name in db[name].index_information():
            if idx_name != "_id_":
                db.command({"collMod": name, "index": {"name": idx_name, "hidden": hidden}})


def _find_execution_stats(node):
    """Busca el primer bloque executionStats dentro de la salida de explain
    (en agregaciones viene anidado en stages[0].$cursor)."""
    if isinstance(node, dict):
        if "executionStats" in node:
            return node["executionStats"]
        for v in node.values():
            found = _find_execution_stats(v)
            if found:
                return found
    elif isinstance(node, list):
        for v in node:
            found = _find_execution_stats(v)
            if found:
                return found
    return None


def explain_find(coll_name, filt, projection=None):
    cmd = {"find": coll_name, "filter": filt}
    if projection:
        cmd["projection"] = projection
    out = db.command({"explain": cmd, "verbosity": "executionStats"})
    return _find_execution_stats(out)


def explain_aggregate(coll_name, pipeline):
    cmd = {"aggregate": coll_name, "pipeline": pipeline, "cursor": {}}
    out = db.command({"explain": cmd, "verbosity": "executionStats"})
    return _find_execution_stats(out)


def _plan_stage(stats):
    """IXSCAN si el plan ganador usó un índice, COLLSCAN si recorrió la colección."""
    return "IXSCAN" if "IXSCAN" in str(stats.get("executionStages", stats)) else "COLLSCAN"


def _measure(steps):
    """Mide una consulta compuesta por uno o varios pasos `find`.

    Cada paso es (colección, función_filtro, proyección, función_siguiente):
    la función_filtro recibe lo que devolvió el paso anterior y arma el
    filtro; función_siguiente extrae de los documentos lo que necesita el
    paso siguiente. Por cada paso se ejecuta la consulta real (tiempo medido
    desde el cliente) y su `explain` con verbosidad executionStats (tiempo en
    el servidor, documentos y llaves examinados, plan). Se reporta la mediana
    de REPEATS ejecuciones."""
    client_ms, server_ms = [], []
    for _ in range(REPEATS):
        carry, t_client, t_server, docs, keys, plans = None, 0.0, 0, 0, 0, []
        for coll_name, filt_fn, projection, next_fn in steps:
            filt = filt_fn(carry)
            t0 = time.perf_counter()
            found = list(db[coll_name].find(filt, projection))
            t_client += (time.perf_counter() - t0) * 1000
            stats = explain_find(coll_name, filt, projection)
            t_server += stats["executionTimeMillis"]
            docs += stats["totalDocsExamined"]
            keys += stats["totalKeysExamined"]
            plans.append(_plan_stage(stats))
            carry = next_fn(found) if next_fn else None
        client_ms.append(t_client)
        server_ms.append(t_server)
    return {
        "tiempo_cliente_ms": round(statistics.median(client_ms), 3),
        "tiempo_servidor_ms": statistics.median(server_ms),
        "docsExamined": docs,
        "keysExamined": keys,
        "pasos": len(steps),
        "plan": " + ".join(plans),
    }


def _queries(sample_original_id, sample_species_id, k):
    """Define las 3 consultas representativas para cada estrategia."""
    kfield = f"kmers.k{k}"
    by_id = lambda _: {"original_id": sample_original_id}
    by_species = lambda _: {"species_id": sample_species_id}
    first_oid = lambda found: found[0]["_id"]
    all_oids = lambda found: [d["_id"] for d in found]

    return {
        # Q1 — punto: perfil de k-mers (k dado) de UNA secuencia.
        "Q1_perfil_kmers_una_secuencia": {
            "embebido": [("bench_embedded", by_id, {kfield: 1}, None)],
            "aparte": [
                ("bench_meta", by_id, {"_id": 1}, first_oid),
                ("bench_kmers_alt", lambda oid: {"sequence_id": oid}, {kfield: 1}, None),
            ],
        },
        # Q2 — rango: perfiles de k-mers de TODAS las secuencias de una especie.
        "Q2_perfiles_kmers_de_una_especie": {
            "embebido": [("bench_embedded", by_species, {kfield: 1, "original_id": 1}, None)],
            "aparte": [
                ("bench_meta", by_species, {"_id": 1}, all_oids),
                ("bench_kmers_alt", lambda oids: {"sequence_id": {"$in": oids}}, {kfield: 1, "sequence_id": 1}, None),
            ],
        },
        # Q3 — combinado: metadatos + perfil de k-mers completo de una secuencia.
        "Q3_metadatos_y_kmers_una_secuencia": {
            "embebido": [("bench_embedded", by_id, None, None)],
            "aparte": [
                ("bench_meta", by_id, None, first_oid),
                ("bench_kmers_alt", lambda oid: {"sequence_id": oid}, None, None),
            ],
        },
    }


def pick_query_targets():
    """Secuencia de ejemplo (la primera de la muestra por original_id) y la
    especie con más secuencias en la muestra, para que Q2 sea un rango real."""
    sample_original_id = db["bench_meta"].find_one({}, {"original_id": 1}, sort=[("original_id", ASCENDING)])["original_id"]
    top = list(db["bench_meta"].aggregate([
        {"$group": {"_id": {"id": "$species_id", "name": "$species_name"}, "n": {"$sum": 1}}},
        {"$sort": {"n": -1, "_id.name": 1}},
        {"$limit": 1},
    ]))[0]
    return sample_original_id, top["_id"]["id"], top["_id"]["name"], top["n"]


def run_queries(sample_original_id, sample_species_id, sample_k=6, sample_kmer="ATGCAT"):
    """Mide las 3 consultas con y sin índice en ambas estrategias, más una
    agregación global (sin índice aplicable) como referencia."""
    queries = _queries(sample_original_id, sample_species_id, sample_k)

    results = {}
    try:
        for use_index in (True, False):
            _set_indexes_hidden(not use_index)
            label = "con_indice" if use_index else "sin_indice"
            for qname, strategies in queries.items():
                for strategy, steps in strategies.items():
                    results.setdefault(qname, {}).setdefault(strategy, {})[label] = _measure(steps)
    finally:
        _set_indexes_hidden(False)

    # Q4 — agregación global: suma del conteo de un k-mer en toda la muestra.
    # Recorre todos los documentos con o sin índice, así que se mide una vez.
    pipe = [{"$group": {"_id": None, "total": {"$sum": {"$ifNull": [f"$kmers.k{sample_k}.{sample_kmer}", 0]}}}}]
    agg = {}
    for strategy, coll_name in (("embebido", "bench_embedded"), ("aparte", "bench_kmers_alt")):
        client_ms, server_ms = [], []
        for _ in range(REPEATS):
            t0 = time.perf_counter()
            list(db[coll_name].aggregate(pipe))
            client_ms.append((time.perf_counter() - t0) * 1000)
            stats = explain_aggregate(coll_name, pipe)
            server_ms.append(stats["executionTimeMillis"])
        agg[strategy] = {
            "tiempo_cliente_ms": round(statistics.median(client_ms), 3),
            "tiempo_servidor_ms": statistics.median(server_ms),
            "docsExamined": stats["totalDocsExamined"],
        }
    results["Q4_suma_global_kmer_(referencia)"] = agg

    return results


def results_table(results):
    """Aplana los resultados de las 3 consultas en filas para mostrarlas como tabla."""
    rows = []
    for qname, strategies in results.items():
        if qname.startswith("Q4"):
            continue
        for strategy, by_index in strategies.items():
            for label, r in by_index.items():
                rows.append({
                    "consulta": qname, "estrategia": strategy, "indice": label,
                    "tiempo_cliente_ms": r["tiempo_cliente_ms"], "tiempo_servidor_ms": r["tiempo_servidor_ms"],
                    "docsExamined": r["docsExamined"],
                    "keysExamined": r["keysExamined"], "pasos": r["pasos"], "plan": r["plan"],
                })
    return rows


def drop_bench_collections():
    for c in BENCH_COLLECTIONS:
        db[c].drop()


if __name__ == "__main__":
    import json

    print(f"Tomando muestra reproducible de {SAMPLE_SIZE} secuencias (semilla {SEED})...")
    docs = get_sample()

    t_emb = load_embedded(docs)
    t_sep = load_separate(docs)
    print(f"Tiempo de carga embebido: {t_emb:.2f} s")
    print(f"Tiempo de carga aparte:   {t_sep:.2f} s")

    print("Almacenamiento:", storage_stats())
    sample_id, species_id, species_name, n = pick_query_targets()
    print(f"Secuencia de ejemplo: {sample_id}; especie para Q2: {species_name} ({n} secuencias)")
    print(json.dumps(run_queries(sample_id, species_id), indent=2, default=str))
    drop_bench_collections()
