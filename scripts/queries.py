"""Consultas obligatorias (sección 4.3 del enunciado) sobre la base `panteon`.

Cada función es una consulta/agregación independiente y reusable, pensada para
llamarse también desde notebooks/02_consultas.ipynb.
"""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]
sequences = db["sequences"]
species = db["species"]


# ---------------------------------------------------------------------------
# Cantidad de elementos
# ---------------------------------------------------------------------------

def q1_count_by_classification():
    """1. ¿Cuántos TEs hay por clase, por orden y por superfamilia en toda la base?"""
    by_class = list(sequences.aggregate([
        {"$group": {"_id": "$te_class", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))
    by_order = list(sequences.aggregate([
        {"$group": {"_id": "$te_order", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))
    by_superfamily = list(sequences.aggregate([
        {"$group": {"_id": "$te_superfamily", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))
    return {"por_clase": by_class, "por_orden": by_order, "por_superfamilia": by_superfamily}


def q2_count_by_species(species_name=None):
    """2. ¿Cuántos TEs tiene cada especie, desglosados por clase, orden y superfamilia?"""
    match = {"$match": {"species_name": species_name}} if species_name else None
    pipeline = []
    if match:
        pipeline.append(match)
    pipeline += [
        {"$group": {
            "_id": {"species": "$species_name", "te_class": "$te_class",
                     "te_order": "$te_order", "te_superfamily": "$te_superfamily"},
            "n": {"$sum": 1},
        }},
        {"$sort": {"_id.species": 1, "n": -1}},
    ]
    return list(sequences.aggregate(pipeline))


def q3_counts_by_kingdom_and_phylum():
    """3. ¿Cómo cambia la cantidad de TEs por clase y orden entre reinos y entre phyla?"""
    base_lookup = [
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
    ]
    by_kingdom = list(sequences.aggregate(base_lookup + [
        {"$group": {
            "_id": {"kingdom": "$sp.kingdom", "te_class": "$te_class", "te_order": "$te_order"},
            "n": {"$sum": 1},
        }},
        {"$sort": {"_id.kingdom": 1, "n": -1}},
    ]))
    by_phylum = list(sequences.aggregate(base_lookup + [
        {"$group": {
            "_id": {"phylum": "$sp.phylum", "te_class": "$te_class", "te_order": "$te_order"},
            "n": {"$sum": 1},
        }},
        {"$sort": {"_id.phylum": 1, "n": -1}},
    ]))
    return {"por_reino": by_kingdom, "por_phylum": by_phylum}


def q4_top_bottom_species(n=10):
    """4. ¿Cuáles son las 10 especies con más TEs y las 10 con menos?"""
    counts = list(sequences.aggregate([
        {"$group": {"_id": "$species_name", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}},
    ]))
    return {"top": counts[:n], "bottom": list(reversed(counts[-n:]))}


# ---------------------------------------------------------------------------
# Longitud y contenido GC
# ---------------------------------------------------------------------------

def q5_length_stats_by_classification():
    """5. Longitud promedio, mínima y máxima de los TEs por clase, orden y superfamilia."""
    def stats_by(field):
        return list(sequences.aggregate([
            {"$group": {
                "_id": f"${field}",
                "avg_length": {"$avg": "$length"},
                "min_length": {"$min": "$length"},
                "max_length": {"$max": "$length"},
                "n": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ]))
    return {
        "por_clase": stats_by("te_class"),
        "por_orden": stats_by("te_order"),
        "por_superfamilia": stats_by("te_superfamily"),
    }


def q6_gc_by_order_and_kingdom():
    """6. Porcentaje de GC promedio por orden y por reino."""
    by_order = list(sequences.aggregate([
        {"$group": {"_id": "$te_order", "avg_gc": {"$avg": "$gc_content"}, "n": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]))
    by_kingdom = list(sequences.aggregate([
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$group": {"_id": "$sp.kingdom", "avg_gc": {"$avg": "$gc_content"}, "n": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]))
    return {"por_orden": by_order, "por_reino": by_kingdom}


def q7_longest_shortest_by_kingdom():
    """7. TEs más largos y más cortos de cada reino (nombre, clasificación, especie).

    Filtra primero los species_id del reino (colección pequeña, 2790 docs) y
    luego usa el índice idx_species_id sobre `sequences`, en vez de hacer un
    $lookup sobre las 240k secuencias por cada reino.
    """
    result = {}
    for kingdom in ("Animalia", "Plantae", "Fungi"):
        species_ids = [doc["_id"] for doc in species.find({"kingdom": kingdom}, {"_id": 1})]
        proj = {"original_id": 1, "te_class": 1, "te_order": 1, "te_superfamily": 1,
                "species_name": 1, "length": 1, "_id": 0}
        longest = list(sequences.find({"species_id": {"$in": species_ids}}, proj).sort("length", -1).limit(1))
        shortest = list(sequences.find({"species_id": {"$in": species_ids}}, proj).sort("length", 1).limit(1))
        result[kingdom] = {"mas_largo": longest[0] if longest else None,
                            "mas_corto": shortest[0] if shortest else None}
    return result


# ---------------------------------------------------------------------------
# Nombres y búsqueda de secuencias
# ---------------------------------------------------------------------------

def q8_search_by_id(original_id):
    """8. Buscar una secuencia por su nombre y mostrar clasificación, especie y taxonomía."""
    pipeline = [
        {"$match": {"original_id": original_id}},
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$project": {
            "_id": 0, "original_id": 1, "te_class": 1, "te_order": 1, "te_superfamily": 1,
            "species_name": 1,
            "taxonomy": {
                "kingdom": "$sp.kingdom", "phylum": "$sp.phylum",
                "taxo_class": "$sp.taxo_class", "taxo_order": "$sp.taxo_order",
                "family": "$sp.family",
            },
        }},
    ]
    result = list(sequences.aggregate(pipeline))
    return result[0] if result else None


def q9_sequence_names_by_superfamily_species(superfamily, species_name):
    """9. Nombres de todas las secuencias de una superfamilia en una especie dada."""
    cursor = sequences.find(
        {"te_superfamily": superfamily, "species_name": species_name},
        {"original_id": 1, "_id": 0},
    )
    return [doc["original_id"] for doc in cursor]


# ---------------------------------------------------------------------------
# Relaciones y calidad
# ---------------------------------------------------------------------------

def q12_lookup_sequences_taxonomy(limit=5):
    """12. Consulta que use $lookup para unir secuencias con la taxonomía de su especie."""
    pipeline = [
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$project": {
            "_id": 0, "original_id": 1, "te_class": 1, "te_order": 1, "te_superfamily": 1,
            "species_name": 1, "kingdom": "$sp.kingdom", "phylum": "$sp.phylum",
        }},
        {"$limit": limit},
    ]
    return list(sequences.aggregate(pipeline))


def q13_comparison_by_source():
    """13. Comparación por origen de los datos (columna Source del CSV)."""
    pipeline = [
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$group": {
            "_id": "$sp.source",
            "n_secuencias": {"$sum": 1},
            "especies": {"$addToSet": "$sp.species_name"},
            "avg_length": {"$avg": "$length"},
        }},
        {"$project": {
            "_id": 1, "n_secuencias": 1, "avg_length": 1,
            "n_especies": {"$size": "$especies"},
        }},
    ]
    results = list(sequences.aggregate(pipeline))
    for r in results:
        r["avg_secuencias_por_especie"] = r["n_secuencias"] / r["n_especies"] if r["n_especies"] else 0
    return results


def q14_quality_control():
    """14. Consulta de control de calidad: secuencias con alto % de N (posible baja calidad)."""
    threshold = 5.0
    high_n = sequences.count_documents({"n_percentage": {"$gt": threshold}})
    total = sequences.count_documents({})
    examples = list(sequences.find(
        {"n_percentage": {"$gt": threshold}},
        {"original_id": 1, "n_percentage": 1, "length": 1, "_id": 0},
    ).sort("n_percentage", -1).limit(10))
    return {
        "umbral_pct_n": threshold,
        "secuencias_sobre_umbral": high_n,
        "total_secuencias": total,
        "porcentaje": round(100 * high_n / total, 4),
        "ejemplos": examples,
    }


# ---------------------------------------------------------------------------
# K-mers
# ---------------------------------------------------------------------------

def q15_kmer_profile(original_id, k):
    """15. Recuperar el perfil de k-mers de una secuencia dada, para un k dado."""
    doc = sequences.find_one(
        {"original_id": original_id},
        {f"kmers.k{k}": 1, "_id": 0, "original_id": 1, "length": 1},
    )
    if not doc:
        return None
    return {"original_id": doc["original_id"], "k": k, "profile": doc.get("kmers", {}).get(f"k{k}", {})}


# ---------------------------------------------------------------------------
# Preguntas propias
# ---------------------------------------------------------------------------

def p1_dominant_superfamily_per_kingdom():
    """Propia 1: ¿Cuál es la superfamilia de TE más frecuente en cada reino?"""
    pipeline = [
        {"$lookup": {"from": "species", "localField": "species_id",
                     "foreignField": "_id", "as": "sp"}},
        {"$unwind": "$sp"},
        {"$group": {"_id": {"kingdom": "$sp.kingdom", "te_superfamily": "$te_superfamily"},
                     "n": {"$sum": 1}}},
        {"$sort": {"_id.kingdom": 1, "n": -1}},
    ]
    rows = list(sequences.aggregate(pipeline))
    best = {}
    for r in rows:
        kingdom = r["_id"]["kingdom"]
        if kingdom not in best:
            best[kingdom] = {"te_superfamily": r["_id"]["te_superfamily"], "n": r["n"]}
    return best


def p2_gc_length_correlation_by_order():
    """Propia 2: ¿Las superfamilias con más contenido GC tienden a tener TEs más largos?"""
    pipeline = [
        {"$group": {
            "_id": "$te_order",
            "avg_gc": {"$avg": "$gc_content"},
            "avg_length": {"$avg": "$length"},
            "n": {"$sum": 1},
        }},
        {"$match": {"n": {"$gte": 30}}},
        {"$sort": {"avg_gc": -1}},
    ]
    return list(sequences.aggregate(pipeline))


if __name__ == "__main__":
    import json
    print(json.dumps(q1_count_by_classification(), indent=2, default=str))
