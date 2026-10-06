# Revisión del Hito 1

Revisión del estado local del proyecto al 5 de octubre de 2026. Fuentes:
`Teoria_de_Compiladores_Trabajo_Parcial_y_Final-1.pdf` (instrucciones y Hito 1,
páginas 1–3), `Grupo 2 Trabajo Parcial Compiladores(1).docx`, código, ejemplos
y pruebas del repositorio.

**Resultado: la entrega todavía no cumple todos los requisitos.** Hay código
para las tres fases y derivaciones verificadas, pero faltan entregables, el
informe requiere correcciones y la integración ANTLR no pudo ejecutarse en
este entorno. Esta revisión no certifica la aprobación del docente ni la
entrega en el aula virtual.

## Contraste con los requisitos

| Requisito | Estado y evidencia |
| --- | --- |
| Grupo de 3–4 integrantes | La carátula enumera tres integrantes. |
| Visto bueno del profesor sobre la idea | No verificable con los archivos disponibles. |
| Herramientas de gestión de proyectos y código | Hay Git, historial y un remoto GitHub configurado. No hay evidencia local suficiente de gestión de tareas/proyecto; no se verificó el estado remoto. |
| Informe de máximo 5 páginas + carátula | La conversión del DOCX con LibreOffice produce 6 páginas totales. El título de la primera sección se desplaza a la carátula: conviene separar esa página y volver a revisar la paginación. |
| Problemática, motivación y objetivos | Presentes en el DOCX, incluidas la aplicación al álgebra lineal y las comprobaciones estáticas de dimensiones. |
| Construcciones con 5 ejemplos cada una en el informe | Parcial: declaraciones, asignaciones, expresiones y selectivas tienen cinco. Iterativas tiene cuatro (1, 2, 4 y 5): falta el tercero. El texto dice cuatro construcciones, aunque enumera cinco. El JSON tiene cinco ejemplos de cada uno de seis grupos, separando `while` y `for`, pero eso no corrige el DOCX. |
| Léxico en formato token: lista de lexemas | Presente en el DOCX y consistente con las reglas de `grammar/AlgaLexer.g4`. |
| Lexer en ANTLR y pruebas con varias entradas | Implementado; hay casos positivos y negativos y pruebas de tokens. Ejecución de integración pendiente en este entorno. |
| GLC por construcción en el informe | Presente y consistente en estructura con `docs/glc.json` y `grammar/AlgaParser.g4`. No se dispone del material de clases para certificar la convención exacta exigida por el profesor. |
| 4 derivaciones más a la izquierda por gramática de construcción | Hay 24 en `docs/04_derivaciones/`: cuatro por grupo, con `while` y `for` separados. Se verificaron. No aparecen en el DOCX ni se remite a ellas; añadir una referencia explícita como documentación complementaria facilitaría su revisión. El PDF no indica explícitamente en esa viñeta que deban insertarse completas en el informe. |
| Parser ANTLR4 y pruebas con varias entradas | Implementado con consumo hasta EOF y casos válidos e inválidos. Ejecución de integración pendiente. |
| Describir por lo menos dos errores semánticos | El DOCX describe variables no declaradas e incompatibilidad de tipos/dimensiones, con ejemplos y correcciones. |
| Implementar y probar por lo menos dos errores semánticos | Hay visitor sobre el árbol ANTLR, tabla de símbolos y reglas de tipos, además de casos de prueba. Las pruebas aisladas de tipos pasan; falta validar el recorrido integrado. |
| Repositorio con archivos G4 y driver simple | Presentes. El remoto configurado es `git@github.com:JeanPool231/alga-compiler.git`; no se certifica publicación ni envío de su URL. |
| Repositorio completo en ZIP | No hay ZIP en esta copia. `scripts/package.py` exige `.gitignore` (ausente) y un PDF sin el sufijo `-1`, por lo que no puede completar el empaquetado tal como está. |
| Todos los artefactos en el repositorio | El PDF y DOCX están en el directorio local, pero Git los muestra como no versionados. Faltan presentación y video. |
| Presentación en PDF | Ausente. Tener `scripts/presentation.py` no satisface el requisito: falta también su entrada `entregables/09_presentacion.json`. |
| Demo en video de máximo 5 minutos | No se encontró video ni referencia a uno en los archivos revisados. |
| Presentación del Hito 1 en semana 7 | Es una condición de entrega que no se puede comprobar desde el código. |

El Hito 1 pide analizadores y semántica parcial. No exige todavía ejecución de
algoritmos numéricos, backend ni generación LLVM; su ausencia no constituye
un incumplimiento de este hito. La originalidad y el dominio del tema durante
la exposición/preguntas tampoco pueden certificarse mediante estas pruebas.

## Validación efectuada

Pasaron 12 pruebas de tipos, 6 pruebas de gramática documental y la comprobación
de las 24 derivaciones:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_types.py' -v
python3 -m unittest discover -s tests -p 'test_glc.py' -v
python3 scripts/derivations.py --check
```

El manifiesto contiene 74 casos (33 sin error y 41 con error esperado).
El programa `05_demo.alga`, que no está en ese manifiesto, tiene su propia
prueba. Existen 75 archivos `.alga` en total. Tener casos definidos no equivale
a haberlos ejecutado satisfactoriamente.

No se ejecutó `test_pipeline.py`: faltan Java, el JAR, el runtime Python
`antlr4` y los módulos generados. Para completar esa verificación, sigue la
instalación del README, genera los analizadores y ejecuta:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Cómo se verifican las derivaciones

`scripts/derivations.py` tokeniza los ejemplos de `docs/ejemplos_informe.json`
y construye un árbol usando `docs/glc.json`. Exige exactamente un árbol que
consuma todos los tokens de cada entrada examinada.

En `derive()`, para cada paso:

1. Localiza el primer símbolo de la forma actual que sea un no terminal.
2. Comprueba que corresponda al nodo que va a expandir.
3. Comprueba que la producción seleccionada exista en la GLC.
4. Sustituye únicamente ese símbolo y recorre sus hijos de izquierda a derecha.
5. Al finalizar, comprueba que no queden no terminales. El llamador verifica
   que la cadena terminal coincida con los tokens del ejemplo original.

`--check` vuelve a generar el contenido esperado en memoria y compara los
Markdown guardados con ese contenido. No es un verificador independiente de
cualquier derivación escrita a mano; generador y comprobación comparten código.
Las comprobaciones internas usan `assert`, así que deben ejecutarse sin
`python -O`. Que estos ejemplos tengan un único árbol no prueba que toda la
gramática sea no ambigua.

Este proceso es independiente del CLI ANTLR. `--phase parse` muestra un árbol
sintáctico, no los pasos de una derivación izquierda. La GLC JSON y la gramática
G4 son dos representaciones que deben mantenerse consistentes.

## Por qué los ejemplos son `.alga`

Son archivos de texto UTF-8; `.alga` identifica el lenguaje por convención.
El driver usa `read_text()` y no restringe la extensión: un archivo `.txt`
con el mismo contenido puede analizarse con el mismo comando.

Las pruebas de integración leen las rutas de `examples/casos.json`, ejecutan
la fase indicada y comparan sus diagnósticos con el resultado esperado. En los
casos negativos sintácticos o semánticos también comprueban que la fase previa
no produzca errores. Algunas pruebas documentales buscan expresamente
`*.alga`, de modo que renombrar los ejemplos exige ajustar el manifiesto y
esos patrones.

## Pendientes concretos

1. Corregir el número de construcciones y agregar el quinto ejemplo iterativo
   en el DOCX; revisar la separación de carátula y la paginación final.
2. Referenciar las derivaciones desde el informe y corregir su enlace a
   `docs/03_gramatica.md`, que no existe.
3. Preparar las dependencias y ejecutar toda la suite ANTLR, guardando evidencia
   de entradas válidas y errores de las tres fases.
4. Preparar la presentación PDF y el video de hasta cinco minutos.
5. Corregir las entradas de empaquetado, producir el ZIP y comprobar su contenido.
6. Versionar los artefactos de entrega y comprobar la publicación y entrega de
   la URL, el ZIP y la evidencia de gestión y aprobación que corresponda.
