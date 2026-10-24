"""Crea la base de datos panteon: colecciones, validación $jsonSchema e índices.

Se puede ejecutar varias veces sin problema (idempotente): si las colecciones
ya existen, solo se asegura de que los índices estén creados.
"""
from pymongo import MongoClient, ASCENDING

client = MongoClient("mongodb://localhost:27017")
db = client["panteon"]

# --- species ---------------------------------------------------------------
species_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["species_name", "kingdom"],
        "properties": {
            "species_name": {"bsonType": "string", "description": "Nombre binomial (o de clado) de la especie, único"},
            "kingdom": {"bsonType": "string", "enum": ["Animalia", "Plantae", "Fungi"]},
            "phylum": {"bsonType": ["string", "null"]},
            "taxo_class": {"bsonType": ["string", "null"]},
            "taxo_order": {"bsonType": ["string", "null"]},
            "family": {"bsonType": ["string", "null"]},
            "source": {"bsonType": ["string", "null"]},
            "source2": {"bsonType": ["string", "null"]},
            "notes": {"bsonType": ["string", "null"]},
        },
    }
}

if "species" not in db.list_collection_names():
    db.create_collection("species", validator=species_schema, validationLevel="moderate")
else:
    db.command({"collMod": "species", "validator": species_schema, "validationLevel": "moderate"})

db["species"].create_index([("species_name", ASCENDING)], unique=True, name="uniq_species_name")
db["species"].create_index([("kingdom", ASCENDING)], name="idx_kingdom")

# --- sequences ---------------------------------------------------------------
sequences_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["original_id", "te_class", "te_order", "te_superfamily", "species_id", "sequence", "length"],
        "properties": {
            "original_id": {"bsonType": "string", "description": "Identificador original PDB..., único"},
            "te_class": {"bsonType": "string"},
            "te_order": {"bsonType": "string"},
            "te_superfamily": {"bsonType": "string"},
            "species_id": {"bsonType": "objectId"},
            "species_name": {"bsonType": "string", "description": "Denormalizado desde species.species_name"},
            "sequence": {"bsonType": "string", "pattern": "^[ACGTN]+$"},
            "length": {"bsonType": "int", "minimum": 1},
            "gc_content": {"bsonType": "double"},
            "n_percentage": {"bsonType": "double"},
            "kmers": {"bsonType": "object"},
        },
    }
}

if "sequences" not in db.list_collection_names():
    db.create_collection("sequences", validator=sequences_schema, validationLevel="moderate")
else:
    db.command({"collMod": "sequences", "validator": sequences_schema, "validationLevel": "moderate"})

db["sequences"].create_index([("original_id", ASCENDING)], unique=True, name="uniq_original_id")
db["sequences"].create_index([("species_id", ASCENDING)], name="idx_species_id")
db["sequences"].create_index(
    [("te_class", ASCENDING), ("te_order", ASCENDING), ("te_superfamily", ASCENDING)],
    name="idx_te_classification",
)

# --- kmer_profiles_alt (solo para el experimento de la sección 4.4) --------
if "kmer_profiles_alt" not in db.list_collection_names():
    db.create_collection("kmer_profiles_alt")
db["kmer_profiles_alt"].create_index([("sequence_id", ASCENDING)], name="idx_sequence_id")

print("Colecciones:", db.list_collection_names())
for coll in ["species", "sequences", "kmer_profiles_alt"]:
    print(f"Índices de {coll}:", list(db[coll].index_information().keys()))
