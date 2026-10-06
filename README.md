# Alga — Hito 1

Analizador léxico, sintáctico y semántico para el lenguaje Alga, orientado a
escalares, vectores y matrices. **Hace análisis estático:** no ejecuta bucles,
no calcula operaciones matriciales y no imprime los argumentos de `print`.

La estructura sigue el laboratorio de MiniLang en
`clases/Ejemplo1 (1)/Ejemplo1/`: `main.py`, analizadores generados en `gen/`,
visitor y tabla de símbolos en `semantic/`, generación con `Makefile` y entradas
`.txt`. La gramática sigue las producciones del DOCX actualizado.

## Requisitos

Instala `python3`, `python3-pip`, Java **11 o superior** y `make`, o los paquetes
equivalentes de tu distribución. También necesitas soporte para `venv`
(`python3-venv` en algunas distribuciones). Los comandos siguientes usan Bash.
`curl` solo es necesario si descargas el JAR desde la terminal.

Ejemplo para Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv default-jre make curl
```

En otras distribuciones los nombres pueden ser `python`, `python-pip` y un
paquete de OpenJDK. Usa un Python 3 vigente; la verificación de esta revisión se
hizo con Python 3.14, Java 17 y ANTLR 4.13.1.

Comprueba las herramientas:

```bash
python3 --version
python3 -m pip --version
java -version
make --version
```

## Preparación

Ejecuta desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Se usa **ANTLR 4.13.1**, tanto el generador Java como
`antlr4-python3-runtime==4.13.1`, para coincidir con la guía de Semana 1.
Si habías instalado 4.13.2 para la versión anterior del proyecto, vuelve a
instalar los requisitos y a generar el código con 4.13.1.

El `Makefile` busca primero el JAR instalado como en clase:

```text
/usr/local/lib/antlr-4.13.1-complete.jar
```

Si no existe, busca `tools/antlr-4.13.1-complete.jar`. Puedes prepararlo así:

```bash
mkdir -p tools
curl -fL https://www.antlr.org/download/antlr-4.13.1-complete.jar \
  -o tools/antlr-4.13.1-complete.jar
```

También puedes indicar otra ubicación del mismo JAR:

```bash
make ANTLR_JAR=/ruta/antlr-4.13.1-complete.jar
```

El generador usa `java -jar`, como los Makefiles del laboratorio. No depende de
los alias `antlr4`, `grun` ni de `CLASSPATH`. La variable `ANTLR_JAR` tiene
prioridad sobre la búsqueda automática; si apunta a una instalación anterior,
usa `unset ANTLR_JAR` o proporciona la ruta correcta.

Genera los analizadores:

```bash
make
```

Esto procesa `grammar/AlgaLexer.g4` y `grammar/AlgaParser.g4`, y crea el lexer,
parser y visitor en `gen/`. Repite `make` cada vez que cambies una gramática.
No edites los módulos generados. El comando anterior
`python3 scripts/generate.py` se conserva como acceso al mismo Makefile.
El runtime instalado con pip no incluye el JAR.

## Analizar un archivo

```bash
python3 main.py test_valid.txt
python3 main.py test_invalid.txt
python3 main.py examples/01_validos/05_demo.txt
```

No necesitas `PYTHONPATH`, instalar el proyecto como paquete ni usar `-m`.
En una nueva terminal, vuelve a activar `.venv` antes de ejecutar Python.
La anterior entrada `python3 -m alga.driver` fue sustituida por `main.py`.

`test_valid.txt` tiene 111 líneas y debe finalizar con:

```text
OK: fase semantic; análisis estático completado
```

`test_invalid.txt` tiene 107 líneas, sintaxis válida y **57 errores semánticos
intencionales**, incluidos errores al principio y al final. Permite comprobar
que se reporta más de un error en la misma ejecución.

Todos los programas de evaluación se guardan como texto UTF-8 con extensión
`.txt`. El analizador lee el contenido; no exige una extensión determinada.
Las rutas relativas se interpretan desde el directorio donde ejecutas el comando.

## Fases y diagnósticos

```bash
python3 main.py test_valid.txt --phase lex
python3 main.py test_valid.txt --phase parse
python3 main.py test_valid.txt --phase semantic
python3 main.py test_invalid.txt --json
python3 main.py --help
```

- `lex`: muestra tokens, lexemas y posiciones.
- `parse`: muestra el árbol sintáctico usando los nombres de reglas del informe
  (`s`, `l`, `d`, `e`, etc.). No muestra una derivación paso a paso.
- `semantic`: revisa nombres, ámbitos, tipos, dimensiones y funciones. Es la
  fase predeterminada.
- `--json`: devuelve `tokens`, `errors` y `tree`; puede combinarse con cada fase.

El orden es léxico → sintáctico → semántico. Si una fase tiene errores, se
reportan y no se ejecuta la siguiente. ANTLR puede recuperarse de errores para
continuar dentro de una fase, pero no garantiza detectar absolutamente todos.
Los diagnósticos tienen el formato `fase:línea:columna: mensaje`, desde 1.

En modo texto los errores van a stderr; con `--json`, los diagnósticos de
análisis aparecen en `errors` por stdout. Los fallos al leer el archivo siempre
van a stderr. Los códigos de salida son:

| Código | Significado |
| --- | --- |
| `0` | Análisis sin errores hasta la fase solicitada. |
| `1` | Se encontraron errores en el programa. |
| `2` | Argumentos incorrectos o archivo ilegible/inexistente. |

## Pruebas

Con el entorno activo, ejecuta:

```bash
make test
```

Este comando regenera los analizadores, ejecuta la suite y verifica las
24 derivaciones. Si ya generaste el código, también puedes usar:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/derivations.py --check
```

La suite tiene **40 pruebas**: incluye los 74 casos del manifiesto, la demo,
los dos programas largos, los 25 ejemplos del DOCX y la correspondencia entre
las producciones del informe, `docs/glc.json` y el parser G4.
Los casos de error pasan cuando aparece el diagnóstico esperado.

Las derivaciones ahora se obtienen del árbol de ANTLR. Cada paso sustituye el
primer no terminal y comprueba que la producción esté en la GLC del informe;
la cadena final se compara con los tokens originales. `--check` compara
además el resultado con los Markdown guardados. Esto no prueba la ausencia
universal de ambigüedad. A diferencia de la versión anterior, esta comprobación
requiere el runtime y los analizadores generados.

Para regenerar los documentos (sobrescribe los seis Markdown):

```bash
make derivations
```

## Organización

| Archivo o carpeta | Función |
| --- | --- |
| `main.py` | Lee el archivo con `FileStream`, crea lexer/parser y ejecuta el visitor. |
| `grammar/AlgaLexer.g4` | Tokens y expresiones regulares del informe. |
| `grammar/AlgaParser.g4` | Producciones del DOCX expresadas en ANTLR. |
| `gen/` | Código generado mediante `make`. |
| `semantic/semantic_visitor.py` | Comprobaciones semánticas sobre el árbol. |
| `semantic/symbol_table.py` | Clases `Symbol` y `SymbolTable` con ámbitos anidados. |
| `semantic/type_rules.py` | Compatibilidad de tipos, dimensiones, funciones e índices. |
| `semantic/errors.py` | Error semántico y captura de diagnósticos ANTLR. |
| `examples/` | Programas válidos, errores por fase y métodos numéricos, todos `.txt`. |
| `examples/casos.json` | Archivo, fase y error esperado de cada caso. |
| `tests/` | Pruebas con `unittest`, incluido en Python. |
| `docs/` | GLC, derivaciones, correspondencia con las clases y revisión del hito. |
| `clases/` | Material de referencia original del profesor. |

Las declaraciones y asignaciones terminan en `;`. Los bloques de control llevan
llaves; el contador del `for` se declara antes de la cabecera. Los comparadores
son `==`, `!=`, `<` y `>`; no hay `<=`, `>=`, `i++` ni comentarios en las entradas
Alga porque no están definidos por su gramática actual.

Los índices empiezan en cero. Se validan los límites de índices literales,
pero no los valores de expresiones dinámicas. Tampoco se analiza inicialización
definitiva, división por cero o convergencia. Son límites del comportamiento
existente, que esta reescritura conserva.

## Entrega y relación con las clases

- [Correspondencia del DOCX con el parser](docs/03_gramatica.md).
- [Referencias de clase y notas sobre elementos adicionales](docs/notas_clases.md).
- [Revisión de todos los requisitos del Hito 1](docs/revision_hito1.md).
- [Ejemplos de métodos numéricos](examples/05_metodos_numericos/README.md).

Para crear `dist/alga_hito1.zip`:

```bash
make package
```

Incluye fuentes, pruebas, entradas `.txt`, documentación, DOCX, PDF de requisitos
y materiales de clase. Excluye entornos virtuales, cachés, JAR y analizadores
generados. Quien lo reciba debe instalar dependencias y ejecutar `make`.
Crear el ZIP **no completa por sí solo el Hito 1**: todavía faltan la presentación
PDF y la demo en video de máximo cinco minutos.

## Problemas frecuentes

| Problema | Solución |
| --- | --- |
| `java: ... not found` | Instala Java y comprueba que `java -version` funcione. |
| Falta ANTLR 4.13.1 | Usa la instalación de clase, descarga el JAR en `tools/` o indica `ANTLR_JAR`. |
| `No module named antlr4` | Activa `.venv` y ejecuta `python3 -m pip install -r requirements.txt`. |
| `No module named gen.AlgaLexer` o `gen.AlgaParser` | Ejecuta `make` antes del programa y las pruebas. |
| Versión del generador distinta del runtime | Usa 4.13.1 para ambos, reinstala los requisitos y ejecuta `make`. |
| `externally-managed-environment` | Instala las dependencias dentro de `.venv`. |
| Falta `venv`/`ensurepip` | Instala el paquete de entornos virtuales correspondiente a tu distribución. |
| `make: ... not found` | Instala `make` o su equivalente en tu distribución. |
| El programa muestra `OK` pero no calcula | Es correcto: esta entrega hace análisis estático. |

Para cerrar el entorno virtual, ejecuta `deactivate`.
