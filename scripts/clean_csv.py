"""Limpieza del CSV de metadatos: columnas requeridas, normalización de nulos y espacios."""
import re
import pandas as pd

REQUIRED_COLS = [
    "Kingdom", "Phylum", "Class", "Order", "Family",
    "Species", "Source", "Source 2", "Notes",
]

# Patrones observados que en realidad significan "dato faltante" (ver docs/data_quality_notes.md)
MISSING_PATTERNS = [
    r"^no trobat$",
    r"^no order.*$",
    r"^no ordre.*$",
    r"^no orden.*$",
    r"^not order identified.*$",
    r".*incertae sedis.*",
]
MISSING_RE = re.compile("|".join(MISSING_PATTERNS), flags=re.IGNORECASE)


def species_match_key(name: str) -> str:
    """Llave normalizada para cruzar especies entre FASTA y CSV.

    Quita puntos (p. ej. 'subsp.' -> 'subsp') y colapsa espacios, para resolver
    las 4 especies que difieren solo en puntuación entre ambos archivos.
    """
    name = name.strip().replace(".", "")
    name = re.sub(r"\s+", " ", name)
    return name.lower()


def load_clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[REQUIRED_COLS].copy()
    df = df.rename(columns={
        "Class": "taxo_class",
        "Order": "taxo_order",
        "Source 2": "source2",
    })
    df = df.rename(columns={c: c.lower() for c in df.columns if c not in ("taxo_class", "taxo_order", "source2")})

    text_cols = ["kingdom", "phylum", "taxo_class", "taxo_order", "family", "species", "source", "source2", "notes"]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()
        df.loc[df[col].str.len() == 0, col] = pd.NA

    for col in ["phylum", "taxo_class", "taxo_order", "family"]:
        is_missing_text = df[col].apply(lambda v: bool(MISSING_RE.match(v)) if pd.notna(v) else False)
        df.loc[is_missing_text, col] = pd.NA

    df["match_key"] = df["species"].apply(species_match_key)

    df = df.where(pd.notna(df), None)
    return df


if __name__ == "__main__":
    df = load_clean_csv("PanTEon_Database_metadata_v1.6.1.csv")
    print(df.shape)
    print(df.head())
    print("Nulos tras limpieza:")
    print(df.isna().sum())
