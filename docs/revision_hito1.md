# Revisión del Hito 1 y de la adaptación a clases

Revisión del 6 de octubre de 2026 sobre el PDF
`Teoria_de_Compiladores_Trabajo_Parcial_y_Final-1.pdf` (páginas 1–3), el DOCX
actualizado `Grupo 2 Trabajo Parcial Compiladores.docx`, los materiales de
`clases/`, el código, las pruebas y los ejemplos locales.

**El analizador y sus pruebas satisfacen los componentes técnicos revisados del
Hito 1. La entrega completa sigue pendiente:** faltan la presentación PDF y el
video. La publicación, aprobación del profesor y exposición no se certifican
mediante pruebas de código.

## Requisitos del PDF

| Requisito | Resultado de la revisión |
| --- | --- |
| Grupo de 3–4 integrantes | La carátula enumera tres integrantes. |
| Visto bueno del profesor sobre la idea | No consta evidencia verificable en los archivos locales. |
| Gestión de proyectos y código fuente | Hay Git, historial y remoto GitHub. No se verificó un tablero ni evidencia equivalente de gestión de tareas. |
| Repositorio GitHub, envío de URL y ZIP | Remoto configurado: `git@github.com:JeanPool231/alga-compiler.git`. El script de ZIP fue corregido y validado. La publicación y el envío de la URL no se verificaron. |
| Todos los artefactos en el repositorio | Las fuentes y documentos disponibles se incluyen al empaquetar. Los cambios locales deben versionarse y publicarse; siguen faltando presentación y video. |
| Informe de máximo 5 páginas + carátula | LibreOffice exporta el DOCX actualizado en 6 páginas totales. El título de la primera sección invade la carátula: revisar esa separación y volver a comprobar el PDF final. |
| Problemática, motivación y objetivos | Presentes en el DOCX. |
| Construcciones con 5 ejemplos por construcción | Corregido en el DOCX recibido: cinco construcciones y cinco ejemplos de cada una. Los 25 ejemplos pasan el parser. |
| Léxico token: lista de lexemas en el informe | Presente. Los tokens, nombres y expresiones regulares se conservan en `AlgaLexer.g4`. |
| Lexer ANTLR y pruebas con varias entradas | Generado y probado con ANTLR 4.13.1. Se verifican entradas válidas y errores léxicos. |
| GLC por construcción y notación de clase | Presente. Las pruebas comparan todas las producciones extraídas del DOCX con `docs/glc.json` y el G4, normalizando nombres y EOF. La notación coincide con las diapositivas de GLC y FIRST/FOLLOW. |
| 4 derivaciones más a la izquierda por construcción | Hay 24 verificadas: cuatro para declaraciones, asignaciones, expresiones y selectivas, y cuatro para cada variante iterativa (`while` y `for`). Están en `docs/04_derivaciones/`; sería conveniente referenciarlas desde el DOCX. La viñeta del PDF no exige explícitamente insertarlas completas en sus cinco páginas. |
| Parser ANTLR4 y varias entradas | Generado y probado. Conserva la sintaxis del informe y exige EOF. |
| Describir por lo menos dos errores semánticos | El DOCX describe uso de variables no declaradas e incompatibilidad de tipos/dimensiones, con ejemplos y correcciones. |
| Implementar y probar por lo menos dos errores semánticos | Visitor y tabla de símbolos verificados. Se conservan también las comprobaciones existentes de ámbitos, duplicados, funciones, condiciones e índices. |
| Código fuente G4 y driver simple | Dos G4 en `grammar/`; entrada directa `python3 main.py archivo.txt`, siguiendo la estructura del laboratorio. |
| Presentación en PDF | Pendiente: no se encontró una presentación de Alga. Los PDF de requisitos y clase no sustituyen este entregable. |
| Demo en video, máximo 5 minutos | Pendiente: no se encontró video ni referencia a una grabación. |
| Presentación del hito en semana 7 | Condición de entrega que no puede verificarse desde el repositorio. |
| Originalidad, exposición y respuestas de la rúbrica | No se pueden certificar con la ejecución de pruebas. Las referencias a clase y las adaptaciones quedan identificadas en `notas_clases.md`. |

El Hito 1 exige el lexer, parser y semántica parcial. No exige todavía backend,
LLVM ni ejecución de operaciones numéricas. Su ausencia no es un incumplimiento
de esta etapa. Los ejercicios adicionales de clase (por ejemplo, cinco errores
por categoría o inicialización definitiva) no se confundieron con los mínimos
del PDF del Hito 1 ni se incorporaron cambiando el lenguaje sin necesidad.

## Validación antes y después

Antes de modificar el código se instalaron las dependencias de la versión
original (ANTLR/runtime 4.13.2) y se ejecutaron las **32 pruebas originales**:
todas pasaron. Se guardó temporalmente el resultado de analizar los 77 archivos
existentes en las fases léxica, sintáctica y semántica.

Después de la reescritura con ANTLR/runtime 4.13.1:

- Pasan **40 pruebas**, incluidas las 32 originales adaptadas a las nuevas rutas.
- Los **74 casos del manifiesto** conservan sus resultados: 33 sin error y
  41 con error esperado. La demo tiene su propia prueba.
- `test_valid.txt` pasa las tres fases. `test_invalid.txt` pasa léxico y sintaxis
  y produce los mismos **57 errores semánticos**, incluido el del final.
- Las **231 comparaciones** (77 archivos × 3 fases) dieron cero diferencias
  en listas de tokens y diagnósticos frente a la versión original.
- Los nombres internos del árbol sí cambian deliberadamente para seguir el
  DOCX; no se afirma igualdad textual de la salida `tree` anterior.
- Se verifican los **25 ejemplos del DOCX**, sus producciones y la correspondencia
  del G4 con `glc.json`.
- Se verifican las **24 derivaciones** y la coincidencia de sus archivos Markdown.
- Hay regresiones para ámbitos hermanos en la misma línea, revisión del cuerpo
  de `while` y ejecución desde otro directorio sin `PYTHONPATH`.

Los casos negativos pasan una prueba cuando el analizador detecta el error
esperado. Estas pruebas no certifican ejecución matemática ni detección de
absolutamente todos los posibles errores.

Comandos reproducibles tras activar el entorno e instalar las dependencias:

```bash
make test
python3 main.py test_valid.txt
python3 main.py test_invalid.txt
make package
```

El comando del ejemplo inválido retorna 1 intencionalmente. La suite completa
retorna 0 cuando todas las comprobaciones pasan. El ZIP debe descomprimirse,
instalar sus dependencias y regenerar los analizadores antes de usarlo.

## Cambios efectuados

- Estructura basada en MiniLang: `main.py`, `gen/`, `semantic/` y `Makefile`.
- Parser con correspondencia directa S/L/D/E/T/F/etc. del DOCX; alternativas
  explícitas para cada operador. `As` se escribe `asig` por compatibilidad con Python.
- Clases sencillas `Type`, `Symbol`, `SymbolTable`, `SemanticVisitor` y
  `SemanticError`; se retiró la `dataclass` y el paquete antiguo `src/alga/`.
- Se renombraron **77 entradas** de `.alga` a `.txt` sin alterar su contenido.
- Las derivaciones se obtienen del árbol de ANTLR; se retiró el parser auxiliar
  con memoización. La comprobación documental ahora necesita ANTLR generado.
- Se corrigió el empaquetador con los nombres reales del DOCX/PDF y la estructura
  nueva. Se retiraron generadores PDF auxiliares sin entradas disponibles.
- Se actualizaron instrucciones, dependencias, rutas y notas de diferencias
  con los laboratorios. El DOCX y los materiales originales de clase no se editaron.

Consulta [notas_clases.md](notas_clases.md) para distinguir las técnicas vistas
en clase de los elementos adicionales necesarios para Alga y la automatización.
