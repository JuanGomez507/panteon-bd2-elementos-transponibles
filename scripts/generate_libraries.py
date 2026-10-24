"""Generación de bibliotecas FASTA a partir de consultas a MongoDB (consultas 10 y 11).

No se lee el archivo original: toda la información sale de la base de datos,
con el mismo formato de encabezado del FASTA original:
    >ID#CLASE/ORDEN/SUPERFAMILIA @Especie
"""
import re
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]
sequences = db["sequences"]
species = db["species"]


def _write_fasta(docs, out_path, line_width=60):
    with open(out_path, "w", encoding="utf-8") as f:
        for doc in docs:
            header = f">{doc['original_id']}#{doc['te_class']}/{doc['te_order']}/{doc['te_superfamily']} @{doc['species_name']}"
            f.write(header + "\n")
            seq = doc["sequence"]
            for i in range(0, len(seq), line_width):
                f.write(seq[i : i + line_width] + "\n")


def library_by_species(species_name: str, out_path: str) -> int:
    """10. Biblioteca de una especie dada, exportada a .fasta."""
    cursor = sequences.find(
        {"species_name": species_name},
        {"original_id": 1, "te_class": 1, "te_order": 1, "te_superfamily": 1,
         "species_name": 1, "sequence": 1, "_id": 0},
    )
    docs = list(cursor)
    _write_fasta(docs, out_path)
    return len(docs)


def library_by_kingdom(kingdom: str, out_path: str) -> int:
    """11. Biblioteca de un reino dado, exportada a .fasta."""
    species_ids = [doc["_id"] for doc in species.find({"kingdom": kingdom}, {"_id": 1})]
    cursor = sequences.find(
        {"species_id": {"$in": species_ids}},
        {"original_id": 1, "te_class": 1, "te_order": 1, "te_superfamily": 1,
         "species_name": 1, "sequence": 1, "_id": 0},
    )
    count = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for doc in cursor:
            header = f">{doc['original_id']}#{doc['te_class']}/{doc['te_order']}/{doc['te_superfamily']} @{doc['species_name']}"
            f.write(header + "\n")
            seq = doc["sequence"]
            for i in range(0, len(seq), 60):
                f.write(seq[i : i + 60] + "\n")
            count += 1
    return count


if __name__ == "__main__":
    import os
    os.makedirs("data/libraries", exist_ok=True)

    n = library_by_species("Halicephalobus mephisto", "data/libraries/Halicephalobus_mephisto.fasta")
    print(f"Biblioteca de especie generada: {n} secuencias -> data/libraries/Halicephalobus_mephisto.fasta")

    n = library_by_kingdom("Fungi", "data/libraries/Fungi.fasta")
    print(f"Biblioteca de reino generada: {n} secuencias -> data/libraries/Fungi.fasta")
