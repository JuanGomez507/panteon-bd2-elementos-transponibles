# Revista elegida y normas aplicadas

## Revista

**BMC Bioinformatics** (BioMed Central, Springer Nature). Tipo de artículo:
**Research article**.

**Por qué encaja:** es una revista de acceso abierto del área de
bioinformática que publica artículos sobre herramientas, modelos y software
para analizar datos biológicos, con una guía de autores pública y detallada.
Se eligió *Research article* y no *Database article* porque, según la propia
guía, un artículo que describe una base de datos pero además incluye
investigación propia (aquí, la evaluación experimental de estrategias de
almacenamiento) debe enviarse como *Research article*.

El artículo se escribió primero para *PLOS Computational Biology* y luego se
migró a BMC Bioinformatics para que su formato fuera distinto al de otros
equipos.

**Guía de autores consultada:**

- Guía general: https://link.springer.com/journal/12859/submission-guidelines
- Research article: https://link.springer.com/journal/12859/submission-guidelines/research-article

## Plantilla LaTeX

Se usó la **plantilla LaTeX oficial de Springer Nature** (`sn-jnl`, versión
3.1, diciembre de 2024), que la guía de BMC recomienda, descargada de
https://www.springernature.com/gp/authors/campaigns/latex-author-support.
En `docs/article/` están la clase `sn-jnl.cls` y el estilo bibliográfico
`sn-vancouver-num.bst`. Opciones de la clase:

- `sn-vancouver-num`: referencias Vancouver numeradas, el estilo de BMC.
- `referee`: doble espacio, como pide BMC.
- `lineno`: números de línea, como pide BMC.
- `\unnumbered`: encabezados sin numerar, como en los artículos de BMC.

## Normas aplicadas en `article.tex`

- **Estructura (Research article):** Título, autores y afiliación, Resumen,
  Palabras clave, Antecedentes, Métodos, Resultados, Discusión, Conclusiones,
  Lista de abreviaturas, Declaraciones y Referencias. El trabajo relacionado
  que exige el enunciado del taller (sección 5.2) va como subsección de
  Antecedentes, que según BMC debe incluir "un resumen de la literatura
  existente".
- **Portada:** nombres completos y dirección institucional de todos los
  autores, con el autor de correspondencia indicado (los tres, con su correo).
- **Resumen:** máximo 350 palabras (314), dividido en *Antecedentes*,
  *Resultados* y *Conclusiones*, sin citas y con pocas abreviaturas.
- **Palabras clave:** entre 3 y 10 (se usaron 7).
- **Uso de modelos de lenguaje:** BMC exige documentarlo en Métodos; se agregó
  la subsección "Uso de herramientas de inteligencia artificial".
- **Declaraciones:** todas las subsecciones obligatorias en el orden de BMC
  (Aprobación ética y consentimiento, Consentimiento para publicación,
  Disponibilidad de datos y materiales, Intereses en conflicto, Financiación,
  Contribuciones de los autores, Agradecimientos), con "No aplica" donde
  corresponde.
- **Disponibilidad de datos y materiales:** cita de los datos con su DOI en
  la lista de referencias y datos del software en el formato de BMC (nombre del
  proyecto, página, sistema operativo, lenguaje, requisitos, licencia).
- **Enlaces web:** BMC pide que los URL vayan como referencias numeradas con
  fecha de consulta y no en el texto; el repositorio del proyecto se cita así.
- **Figuras:** citadas como "Fig. 1", "Fig. 2", ... en orden de aparición, con
  título corto (máx. 15 palabras) y leyenda. BMC pide subir las imágenes como
  archivos aparte; aquí se incluyen en el PDF porque el enunciado del taller
  exige que el artículo muestre las figuras. Los archivos están en
  `docs/article/figures/`.
- **Tablas:** numeradas en orden de cita, con título encima, sin color ni
  sombreado y sin comas en los números (los miles se separan con un espacio
  fino, por ejemplo 239 946).
- **Referencias:** estilo Vancouver numerado, en el orden en que se citan por
  primera vez.

## Nota sobre el idioma

El artículo se escribió en español (opción permitida por la sección 5.1 del
enunciado del taller) sobre la plantilla oficial de Springer Nature; BMC
publica en inglés, pero el taller autoriza explícitamente español o inglés.
Algunos textos fijos del estilo bibliográfico ("Available from", "cited")
quedan en inglés porque los genera `sn-vancouver-num.bst`.
