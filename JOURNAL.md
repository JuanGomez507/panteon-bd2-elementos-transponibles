# Revista elegida y normas aplicadas

## Revista

**PLOS Computational Biology** (Public Library of Science).

**Por qué encaja:** es una revista de referencia en bioinformática computacional,
de acceso abierto, con una guía de autores pública y detallada (a diferencia de
otras opciones evaluadas del enunciado — *BMC Bioinformatics* y *Database:
The Journal of Biological Databases and Curation*, ambas del grupo
Springer/Oxford, cuyas páginas de "submission guidelines" exigen inicio de
sesión institucional y no pudieron consultarse directamente). PLOS Comp Biol
además pide explícitamente una sección de *Materials and Methods* y acepta
artículos centrados en metodología/infraestructura de datos, que es exactamente
el tipo de contribución de este proyecto (diseño de una base de datos, no un
hallazgo biológico nuevo).

**Guía de autores consultada:**
https://journals.plos.org/ploscompbiol/s/submission-guidelines

## Normas aplicadas en `article.tex`

- **Estructura:** Título, Autores/Afiliaciones, Resumen (Abstract), Resumen para
  el lector no especializado (Author Summary), Introducción, Materiales y
  Métodos, Resultados, Discusión, Conclusiones, Disponibilidad de datos y
  código, Agradecimientos, Referencias. PLOS permite colocar Materiales y
  Métodos antes de Resultados/Discusión siempre que se justifique; aquí se
  colocó antes, siguiendo la estructura sugerida explícitamente en la sección
  5.2 del enunciado del taller.
- **Resumen (Abstract):** máximo 300 palabras, sin subtítulos (Background/
  Methods/Conclusions), sin citas, sin abreviaturas especializadas sin definir.
- **Author Summary:** 150–200 palabras, en lenguaje no técnico.
- **Título:** en oración (sentence case), ≤200 caracteres; se incluyó además un
  título corto ≤70 caracteres.
- **Figuras:** numeradas en orden de cita ("Fig 1", "Fig 2", ...), con la
  leyenda ubicada inmediatamente después del párrafo donde se citan por primera
  vez (no al final del documento).
- **Tablas:** numeradas en orden de cita ("Table 1", ...), con el título encima
  y las notas debajo; incluidas en el cuerpo del texto, no como archivos aparte.
- **Referencias:** estilo Vancouver (numérico, ICMJE), en el orden en que se
  citan por primera vez, entre corchetes (p. ej. "[1]"); hasta seis autores y
  luego "et al."; DOI completo cuando está disponible.
- **Formato general:** texto a doble espacio, numeración continua de líneas
  (paquete `lineno`), sin notas al pie, abreviaturas definidas en su primer uso.
- **Disponibilidad de datos y código:** sección obligatoria con el enlace al
  repositorio del equipo y la cita de los datos originales (PanTEon Database).

## Nota sobre el idioma

El artículo se escribió en español (opción permitida por la sección 5.1 del
enunciado del taller). La plantilla LaTeX usada reproduce la estructura y el
formato exigidos por PLOS Computational Biology, adaptando el idioma del
contenido; PLOS publica normalmente en inglés, pero el taller autoriza
explícitamente español o inglés para este trabajo académico.
