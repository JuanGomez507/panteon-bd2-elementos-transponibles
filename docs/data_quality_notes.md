# Notas de calidad de datos — PanTEon Database v1.6.1

Resultado de la exploración inicial (fase de diseño). Sirve de insumo para el pipeline de
limpieza y para la sección de "Materiales y métodos" del artículo.

## FASTA (`PanTEon_Database_v1.6.1.fasta`)

- **239,946 secuencias**, todas con encabezado bien formado (0 encabezados inválidos,
  patrón `>ID#CLASE/ORDEN/SUPERFAMILIA @Especie`).
- **0 IDs duplicados**.
- Jerarquía de clasificación: **2 clases** (CLASSI, CLASSII), **11 órdenes**, **66 superfamilias**.
- **2790 especies distintas** en el FASTA.
- Longitudes: mínimo 81 nt, máximo 19,926 nt, media ≈ 4017 nt, mediana ≈ 4259 nt.
- **Alfabeto de nucleótidos**: estrictamente `{A, C, G, T, N}` una vez normalizado a
  mayúsculas — no aparecen otros códigos IUPAC de ambigüedad.
- **Mayúsculas/minúsculas mezcladas entre secuencias**: cada secuencia individual es
  *consistentemente* mayúscula o minúscula (no se mezclan mayúscula/minúscula dentro
  de un mismo registro), pero el archivo combina ambos estilos entre registros distintos.
  → Acción: normalizar todo a mayúsculas al leer.
- **Presencia de N**: ~35% de las secuencias (muestra de 20k) tienen al menos una N,
  en promedio ~1.1% de la longitud en las que la tienen; un caso observado llega a ~50% N.
  Ninguna secuencia es 100% N.
  → Acción: calcular `%N` como atributo por secuencia; al generar k-mers, descartar
  cualquier k-mer que contenga un carácter distinto de A/C/G/T (no se "rellenan" ni se
  cuentan como un símbolo más del alfabeto).

## CSV (`PanTEon_Database_metadata_v1.6.1.csv`)

- 2790 filas (una por especie), 13 columnas en el archivo original; el proyecto solo
  usa 9: `Kingdom, Phylum, Class, Order, Family, Species, Source, Source 2, Notes`.
- **Reinos**: Fungi (1559), Animalia (780), Plantae (451).
- **Source**: RM2+MCH (2404), Dfam (386).
- **Sin especies duplicadas** en la columna `Species`.
- **Valores faltantes reales** (`NaN`): Phylum (3), Class (49), Order (29), Family (76).
- **Valores faltantes disfrazados de texto** en `Order` (y variantes en otras columnas):
  cadenas como `"No trobat"`, `"No order"`, `"No ordre NCBI"`, `"No Orden No trobat"`,
  `"Not order identified <Clase>"`, frases con `"incertae sedis"`.
  → Acción: normalizarlas a `null` en la limpieza (lista de patrones conocida).
- **45 filas** cuyo campo `Species` no es un binomio (género + epíteto) sino un **taxón
  superior** (p. ej. `Primates`, `Rodentia`, `Mammalia`, `Homininae`, `Teleostei`).
  Todas tienen `Source = Dfam` — corresponden a bibliotecas de consenso a nivel de
  clado, no a especies individuales.
  → Acción: documentarlo explícitamente en el modelo (el campo `Species` puede
  contener un nombre de clado cuando `Source = Dfam` ancestral); no se excluyen,
  pero se señalan en el informe de calidad y en el artículo.

## Cruce FASTA ↔ CSV (por especie)

- Mismo número de especies en ambos lados (2790), pero **4 no cruzan por un problema
  de formato**: el FASTA usa abreviaturas con punto (`subsp.`, `sp.`) y el CSV las mismas
  sin punto (`subsp`, `sp`):
  - `Abrus pulchellus subsp. cantoniensis` vs `Abrus pulchellus subsp cantoniensis`
  - `Beta vulgaris subsp. vulgaris` vs `Beta vulgaris subsp vulgaris`
  - `Coccomyxa sp. obi` vs `Coccomyxa sp obi`
  - `Marchantia polymorpha subsp. montivagans` vs `Marchantia polymorpha subsp montivagans`
  → Acción: normalizar la llave de cruce quitando los puntos (o unificando a un único
  estilo) antes de hacer el join; documentar el caso en el artículo como hallazgo de
  calidad de datos.
- Tras esa normalización, **las 2790 especies cruzan exactamente** (0 huérfanas en
  cualquiera de los dos lados).
