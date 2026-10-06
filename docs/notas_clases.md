# Adaptación a los ejemplos de clase

## Referencias utilizadas

La referencia principal para la organización del programa es
[MiniLang con análisis semántico](<../clases/Ejemplo1 (1)/Ejemplo1/main.py>), junto
con su [visitor](<../clases/Ejemplo1 (1)/Ejemplo1/semantic/semantic_visitor.py>),
[tabla de símbolos](<../clases/Ejemplo1 (1)/Ejemplo1/semantic/symbol_table.py>),
[errores](<../clases/Ejemplo1 (1)/Ejemplo1/semantic/errors.py>) y
[Makefile](<../clases/Ejemplo1 (1)/Ejemplo1/Makefile>).

También se revisaron los laboratorios léxicos de `clases/Ejemplos/`, los ejemplos
Oracion y Calc de `clases/Ejemplos (1)/Ejemplos/`, MiniLang sintáctico,
`SimpleLexer.g4`, las guías de Semanas 1 y 6 y los PDF de léxico, sintaxis,
ambigüedades, FIRST/FOLLOW y semántica. Los dos PDF de ambigüedades tienen el
mismo texto extraído. Los archivos del profesor se conservan sin cambios.

| En clase | En Alga |
| --- | --- |
| `FileStream(archivo, encoding='utf-8')` | `main.py` lee los programas `.txt` de la misma forma. |
| `lexer → CommonTokenStream → parser → regla inicial` | Mismo flujo; la regla inicial es `s()`, que corresponde a S en el informe. |
| `stream.fill()` y bucle sobre tokens | La fase léxica completa la entrada y registra cada token y su posición. |
| `tree.toStringTree(recog=parser)` | Salida de `--phase parse`. |
| `InputStream` en Calc | Entrada de cadenas desde las pruebas mediante `analyze()`. |
| `SemanticVisitor` generado a partir de `-visitor` | Visitor en `semantic/semantic_visitor.py`. |
| `Symbol`, `SymbolTable`, pila de ámbitos y diccionarios | Misma separación en `semantic/symbol_table.py`. |
| `SemanticError` y lista `visitor.errors` | Mismo mecanismo, conservando línea y columna de los diagnósticos de Alga. |
| Tipos devueltos por métodos `visit...` | El visitor devuelve el tipo de cada expresión; Alga incluye su dimensión. |
| Makefile, ANTLR 4.13.1 y carpeta `gen/` | Misma versión y organización para generar los analizadores. |

## Qué se confirma del DOCX

El DOCX usa la notación de GLC de las clases: S como inicio, alternativas con
`|`, ε y los no terminales E, T y F. En particular, `E → T E′` y `T → F T′`
coinciden con la eliminación de recursividad izquierda explicada en
`clases/Ambiguedades.pdf` (diapositivas 9–11) y con el ejemplo de
`clases/CalculoFirstFollow.pdf` (sección 2).

No es literalmente la misma gramática de los laboratorios: Calc y MiniLang
usan recursión izquierda directa en expresiones, y MiniLang tiene `var`, `:=`,
`then`, `do`, etc. ANTLR acepta esa forma. Reemplazar la sintaxis de Alga por la
de MiniLang cambiaría el lenguaje del informe. Por eso se conserva **la GLC
exacta del DOCX**, mientras se adapta la organización Python al laboratorio.

La correspondencia está en [03_gramatica.md](03_gramatica.md). Hay pruebas que
comparan las producciones extraídas del DOCX, el JSON documental y el G4,
normalizando solamente los nombres y el marcador EOF. Los 25 ejemplos del
DOCX pasan el análisis sintáctico. Muchos son fragmentos con identificadores
sin declarar: no se exige que pasen semántica aislados.

## Elementos adicionales necesarios

Estos detalles no se presentan como copias de código enseñado en clase:

1. **Tipos y dimensiones de Alga.** `Type` es una clase Python sencilla, como
   `Symbol`; reemplaza la anterior `dataclass`. Su atributo `shape` y las reglas
   de `type_rules.py` permiten distinguir `matrix[2][3]` de `matrix[3][2]`.
   MiniLang solo necesita tipos básicos, pero Alga requiere además producto
   matricial, funciones algebraicas, aridad, literales e indexación.
2. **Índices literales exactos.** `re` y `Decimal` comprueban índices firmados
   sin errores de redondeo. No ejecutan expresiones ni prueban límites dinámicos.
3. **Captura de errores ANTLR.** `DiagnosticListener` hereda de `ErrorListener`
   para conservar múltiples diagnósticos y detener las fases siguientes si
   hubo errores. Los ejemplos básicos imprimen los mensajes predeterminados.
4. **Opciones y salida estructurada.** `argparse`, JSON y códigos de salida
   conservan `--phase`, `--json` y los resultados 0/1/2 ya existentes. Son
   utilidades de la biblioteca estándar, no algoritmos adicionales de compilación.
5. **Lexer y parser separados.** `tokenVocab=AlgaLexer` conecta los dos G4
   solicitados. Los ejemplos de clase incluyen lexers independientes y gramáticas
   combinadas. Se mantienen los nombres de token del DOCX. `EOF` se agrega a S,
   como en MiniLang, para impedir que se acepte solo un prefijo del archivo.
6. **Recorrido de reglas con prima.** El visitor acumula operaciones de izquierda
   a derecha en E′/T′ para conservar la asociatividad de `-` y `/`. Cambiarlo por
   una evaluación de derecha a izquierda cambiaría el comportamiento. Los bucles
   sobre listas y colas también evitan recursión Python adicional en el visitor;
   la gramática sigue siendo recursiva.
7. **Verificación documental.** `scripts/derivations.py` recorre el árbol de
   ANTLR y lo expresa con los símbolos del DOCX. Usa `getRuleIndex`,
   `getChildren`, un mapa de nombres y selección de la regla inicial para las
   derivaciones por construcción. Se retiró el segundo parser por memoización.
   No se demuestra con ello que toda la gramática sea no ambigua.
8. **Automatización de evaluación.** `unittest`, lectura de XML dentro del DOCX,
   archivos temporales y ZIP se usan en pruebas o empaquetado. Permiten comprobar
   que la reescritura conserve los casos, corresponda al documento y se pueda
   entregar. No intervienen en el análisis normal de `python3 main.py archivo.txt`.

Los flags `-no-listener` y `-Werror` evitan generar una clase que no se utiliza y
hacen fallar la generación si ANTLR encuentra advertencias. Son opciones de la
misma herramienta. La búsqueda del JAR local y la opción `ANTLR_JAR` permiten
usar tanto la instalación de clase como una instalación sin permisos de sistema.

## Diferencias intencionales con los ejercicios

- Cada bloque recibe un ámbito único, incluso si comparte línea con otro.
  Nombrar ambos bloques `if_L<línea>`, como en el ejemplo, puede mezclar sus
  declaraciones. Se conserva el aislamiento que ya tenía Alga.
- El cuerpo de `while` siempre se visita una vez. En el visitor de clase, su
  visita aparece indentada dentro del caso de condición incorrecta. Copiar esa
  indentación impediría verificar el cuerpo cuando la condición es válida.
- El ejemplo Calc ambiguo es didáctico: su propio README muestra un resultado
  incorrecto para `2+3*4`. Se conserva la precedencia E/T/F del informe y del
  ejemplo Calc corregido.
- No se agrega `OTRO : .` para ignorar caracteres desconocidos: Alga debe
  denunciarlos como errores léxicos. Tampoco se introducen comentarios,
  notación científica u operadores que no estén definidos en el DOCX.
- No se incorporan avisos de variables sin usar ni errores de inicialización
  definitiva/división por cero propuestos para MiniLang: cambiarían el alcance
  y los resultados de Alga. Son posibles ampliaciones, no parte de esta migración.

## Limpieza y compatibilidad

Se sustituyó `src/alga/` por la estructura de raíz usada en los laboratorios.
La entrada pública es `python3 main.py archivo.txt`; ya no se usa
`python3 -m alga.driver` ni `PYTHONPATH=src`. Las 77 entradas existentes se
renombraron sin cambiar sus contenidos, y se actualizaron rutas y pruebas.

Se retiraron `guide_pdf.py` y `presentation.py`: eran generadores auxiliares
con Cairo/ctypes y construcción manual de PDF, ajenos al analizador, cuyas
entradas ni siquiera estaban incluidas. Su eliminación no sustituye la
presentación y el video que todavía deben prepararse para la entrega.
Se retiraron también los cachés Python versionados y se añadió `.gitignore`.

Se mantienen 24 derivaciones: cuatro para cada grupo de declaraciones,
asignaciones, expresiones, selectivas, `while` y `for`. El informe trata las dos
últimas como una sola construcción, iterativas. El JSON conserva ejemplos
adicionales de ambos bucles; incluye el nuevo ejemplo `while (norm(v) > 1)` del
DOCX. El texto del DOCX no se modificó durante esta adaptación.
