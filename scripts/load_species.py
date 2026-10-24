"""Carga la colección species a partir del CSV limpio. Idempotente (upsert por species_name)."""
from pymongo import MongoClient, UpdateOne
from clean_csv import load_clean_csv

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]


def load_species(csv_path="PanTEon_Database_metadata_v1.6.1.csv"):
    df = load_clean_csv(csv_path)
    ops = []
    for row in df.to_dict(orient="records"):
        match_key = row.pop("match_key")
        doc = {
            "species_name": row["species"],
            "match_key": match_key,
            "kingdom": row["kingdom"],
            "phylum": row["phylum"],
            "taxo_class": row["taxo_class"],
            "taxo_order": row["taxo_order"],
            "family": row["family"],
            "source": row["source"],
            "source2": row["source2"],
            "notes": row["notes"],
        }
        ops.append(UpdateOne({"species_name": doc["species_name"]}, {"$set": doc}, upsert=True))

    if ops:
        result = db["species"].bulk_write(ops, ordered=False)
        print(f"Upserted: {result.upserted_count}, modified: {result.modified_count}, matched: {result.matched_count}")

    db["species"].create_index("match_key", name="idx_match_key")
    return db["species"].count_documents({})


if __name__ == "__main__":
    n = load_species()
    print(f"Total especies en la colección: {n}")
