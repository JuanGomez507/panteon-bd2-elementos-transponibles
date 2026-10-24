"""Cálculo de perfiles de k-mers para k=1..6, como diccionario disperso de conteos.

Los k-mers que contienen cualquier carácter distinto de A/C/G/T se descartan
(no se cuentan): no se "rellenan" ni se tratan como un símbolo más del alfabeto,
solo se excluyen de los conteos (ver docs/data_quality_notes.md).
"""
from collections import Counter

VALID = set("ACGT")


def kmer_profiles(sequence: str, ks=range(1, 7)) -> dict:
    """Devuelve {"k1": {...}, "k2": {...}, ..., "k6": {...}} con conteos dispersos."""
    profiles = {}
    for k in ks:
        counts = Counter()
        for i in range(len(sequence) - k + 1):
            sub = sequence[i : i + k]
            if VALID.issuperset(sub):
                counts[sub] += 1
        profiles[f"k{k}"] = dict(counts)
    return profiles


def gc_content(sequence: str) -> float:
    if not sequence:
        return 0.0
    gc = sequence.count("G") + sequence.count("C")
    return 100.0 * gc / len(sequence)


def n_percentage(sequence: str) -> float:
    if not sequence:
        return 0.0
    return 100.0 * sequence.count("N") / len(sequence)
