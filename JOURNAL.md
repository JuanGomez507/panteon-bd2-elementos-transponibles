# Revista elegida y normas aplicadas

## Revista

Elegimos **BMC Bioinformatics** (BioMed Central, Springer Nature) en la modalidad de **Research article**.

**Por qué la elegimos:** Es una revista de acceso abierto bastante conocida en bioinformática que publica herramientas y modelos para datos biológicos. Su guía de autores es pública y clara. Escogimos *Research article* en lugar de *Database article* porque la misma guía aclara que si el trabajo incluye experimentos propios (como las pruebas de rendimiento que hicimos midiendo el almacenamiento), debe enviarse como un artículo de investigación normal.

Inicialmente la plantilla estaba planteada para *PLOS Computational Biology*, pero decidimos pasarla a BMC Bioinformatics para tener un formato diferente al de los demás grupos.

**Enlaces a las guías consultadas:**
- Guía general: https://link.springer.com/journal/12859/submission-guidelines
- Guía de Research article: https://link.springer.com/journal/12859/submission-guidelines/research-article

## Plantilla LaTeX usada

Usamos la plantilla oficial de Springer Nature (`sn-jnl`, versión 3.1 de diciembre de 2024) en `docs/article/`, incluyendo el estilo bibliográfico `sn-vancouver-num.bst`. Opciones que configuramos en la clase:

- `sn-vancouver-num`: Citas numeradas en formato Vancouver.
- `referee`: Texto a doble espacio.
- `lineno`: Números de línea para facilitar la revisión.
- `\unnumbered`: Títulos y secciones sin numeración.

## Normas aplicadas en el `article.tex`

- **Estructura:** Título, autores, afiliación, Resumen, Palabras clave, Antecedentes, Métodos, Resultados, Discusión, Conclusiones, Abreviaturas, Declaraciones y Referencias. El trabajo relacionado se incluyó dentro de *Antecedentes*.
- **Portada:** Nombres completos, universidad y correos institucionales de los tres integrantes.
- **Resumen:** 314 palabras (el máximo es 350), organizado en *Antecedentes*, *Resultados* y *Conclusiones*, sin citas bibliográficas.
- **Palabras clave:** Incluimos 7 términos.
- **Uso de IA:** Agregamos la sección obligatoria en Métodos para declarar el uso de asistentes de lenguaje en partes del código y las figuras.
- **Declaraciones:** Incluimos todos los bloques requeridos por la revista (Ética, Consentimiento, Disponibilidad de datos, Conflictos de interés, Financiación, Contribuciones de los autores y Agradecimientos).
- **Datos y repositorio:** Citamos la base PanTEon con su DOI y registramos el repositorio en el formato exigido por BMC.
- **URLs:** Las direcciones web van como referencias numeradas en la bibliografía y no sueltas en el texto.
- **Figuras:** Van numeradas como "Fig. 1", "Fig. 2", etc., con su respectivo título y leyenda. Aunque la revista pide subirlas por separado, las dejamos incrustadas en el PDF para cumplir la entrega del taller.
- **Tablas:** Van sin bordes verticales ni sombreados, con el título arriba y los miles separados por espacio fino (ejemplo: 239 946).
- **Citas:** Estilo Vancouver numerado por orden de aparición.

## Nota sobre el idioma

El artículo está en español (opción autorizada en la guía del taller). Como la plantilla de Springer Nature está diseñada para publicaciones en inglés, algunos textos automáticos de la bibliografía (como "Available from" o "cited") quedan en inglés por el compilador `.bst`.

