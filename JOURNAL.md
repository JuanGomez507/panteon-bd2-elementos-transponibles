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

## Plantilla LaTeX

El artículo usa la **plantilla LaTeX oficial de PLOS** (versión 3.8, abril de
2026), descargada de https://journals.plos.org/ploscompbiol/s/latex
(`PLOS_latex_template.zip`). Se conservó su preámbulo completo (la plantilla
prohíbe eliminar paquetes) y el estilo bibliográfico oficial `plos2025.bst`,
incluido en `docs/article/`. Adaptaciones mínimas:

- `\DisableLigatures` de `microtype` solo existe en pdfLaTeX; se dejó dentro de
  un `\ifPDFTeX` para que el artículo también compile con XeTeX (`tectonic`).
  Con pdfLaTeX (por ejemplo en Overleaf) se comporta igual que la plantilla.
- Las tablas se rotulan "Tabla" (el texto está en español); las figuras
  conservan "Fig", como exige PLOS.

## Normas aplicadas en `article.tex`

- **Estructura:** Título, Autores/Afiliaciones, Resumen (Abstract), Resumen para
  el lector no especializado (Author Summary), Introducción, Trabajo
  relacionado, Materiales y Métodos, Resultados, Discusión, Conclusiones,
  Disponibilidad de datos y código, Agradecimientos, Referencias. PLOS no
  define una sección de "Trabajo relacionado"; se agregó como sección propia
  justo después de la Introducción porque el enunciado del taller (sección 5.2)
  la exige. Materiales y Métodos va antes de Resultados, como en la plantilla.
- **Portada:** como en la plantilla, el título, los autores, la afiliación, el
  Resumen y el Author Summary van en la primera página; el cuerpo empieza en
  página nueva con márgenes completos y numeración de líneas.
- **Autores:** sin títulos ni cargos (norma de PLOS); contribución igual marcada
  con el símbolo de la plantilla y correos de contacto en la nota con
  asterisco. El curso y el docente se mencionan en Agradecimientos.
- **Resumen (Abstract):** máximo 300 palabras (268), sin subtítulos, sin citas.
- **Author Summary:** 150–200 palabras (150), en primera persona y lenguaje no
  técnico.
- **Título:** en oración (sentence case), ≤250 caracteres (143).
- **Figuras:** "Fig 1", "Fig 2", ... en orden de cita, con la leyenda justo
  después del párrafo donde se citan por primera vez. PLOS pide que en un envío
  real las imágenes se suban como archivos aparte y no dentro del PDF; aquí se
  incluyen en el PDF porque el enunciado del taller exige que el artículo
  muestre las figuras con su interpretación. Los archivos individuales están en
  `docs/article/figures/`.
- **Tablas:** basadas en celdas, con el estilo de bordes de la plantilla, el
  título encima y ubicadas después del párrafo donde se citan.
- **Referencias:** estilo Vancouver con `plos2025.bst`, numeradas en orden de
  primera cita; DOI completo cuando está disponible.
- **Formato general:** espaciado sencillo (el doble espaciado es opcional en la
  plantilla), numeración continua de líneas, sin notas al pie, sin color en el
  texto, abreviaturas definidas en su primer uso.
- **Disponibilidad de datos y código:** sección con el enlace al repositorio
  del equipo y la cita de los datos originales (PanTEon Database).

## Nota sobre el idioma

El artículo se escribió en español (opción permitida por la sección 5.1 del
enunciado del taller) sobre la plantilla oficial de PLOS Computational Biology;
PLOS publica normalmente en inglés, pero el taller autoriza explícitamente
español o inglés para este trabajo académico.
