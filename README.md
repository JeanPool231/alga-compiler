# Alga Compiler

Front-end de Alga (Hito 1), implementado en Python y ANTLR 4. Realiza análisis
léxico, sintáctico y semántico de programas con escalares, vectores, matrices,
condicionales y bucles.

**Actualmente hace análisis estático:** no ejecuta los programas `.alga`, no
calcula resultados numéricos ni genera ejecutables. Una llamada a `print` en
Alga se valida, pero no imprime su argumento.

## Requisitos

Instala los siguientes paquetes del sistema, o sus equivalentes según tu
distribución:

- `python3`: Python **3.9 o superior** (el código usa anotaciones como `tuple[int, ...]`).
- `python3-pip`: gestor de dependencias de Python.
- Java: un JRE/JDK compatible con ANTLR 4.13.2, con el comando `java` en el `PATH`.
- Soporte para entornos virtuales (`venv`); algunas distribuciones lo separan
  en el paquete `python3-venv`.
- `curl`, si quieres descargar el JAR con el comando indicado más abajo.
  También puedes descargarlo desde el navegador.

Por ejemplo, en Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv default-jre curl
```

En otras distribuciones los nombres pueden ser `python`, `python-pip`,
`jre-openjdk` o un paquete de OpenJDK con versión. Lo necesario es disponer de
un intérprete Python compatible, pip, venv y Java. Si tu intérprete se llama
`python`, adapta los comandos siguientes.

Comprueba la instalación:

```bash
python3 --version
python3 -m pip --version
java -version
```

## Instalación y generación de los analizadores

Ejecuta los comandos desde la **raíz del repositorio**, donde están
`requirements.txt`, `grammar/` y `scripts/`. Los ejemplos usan Bash o una shell
compatible en Linux.

### 1. Preparar Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

La dependencia Python es `antlr4-python3-runtime==4.13.2`. Este paquete es el
runtime que usan los analizadores generados; **no incluye el generador Java**.
Usa el entorno virtual también al ejecutar el proyecto y las pruebas.

### 2. Colocar ANTLR en `./tools`

El JAR no viene incluido. Por defecto, `scripts/generate.py` busca exactamente:

```text
tools/antlr-4.13.2-complete.jar
```

La ruta se calcula respecto a la raíz del proyecto. Crea la carpeta y descarga
el JAR completo de ANTLR 4.13.2:

```bash
mkdir -p tools
curl -fL https://www.antlr.org/download/antlr-4.13.2-complete.jar \
  -o tools/antlr-4.13.2-complete.jar
```

**La instalación global utilizada en los ejemplos del profesor no se detecta
automáticamente.** El script invoca `java -jar` sobre ese archivo; no utiliza
el comando o alias `antlr4`, `grun` ni la configuración de `CLASSPATH`.

Si ya tienes el JAR **4.13.2** en otra carpeta, puedes reutilizarlo sin copiarlo
a `tools/`, indicando su ruta mediante `ANTLR_JAR`:

```bash
ANTLR_JAR="/ruta/al/antlr-4.13.2-complete.jar" python3 scripts/generate.py
```

Usa la misma versión para el JAR y el runtime de Python. Cambiar solamente el
nombre de un JAR de otra versión no lo hace compatible. Si tienes `ANTLR_JAR`
definida, esta tiene prioridad sobre `tools/`; usa `unset ANTLR_JAR` para volver
a la ubicación predeterminada.

### 3. Generar el lexer, parser y visitor

Si usas la ubicación predeterminada:

```bash
python3 scripts/generate.py
```

El script procesa primero `grammar/AlgaLexer.g4` y después
`grammar/AlgaParser.g4`, y escribe los módulos Python en `src/alga/generated/`.
Este paso es obligatorio antes de usar el CLI o las pruebas de integración.
Repítelo si modificas las gramáticas. Java y el JAR se necesitan para generar;
el análisis posterior utiliza Python y su runtime de ANTLR.

## Uso

Con el entorno virtual activo, analiza el ejemplo principal:

```bash
PYTHONPATH=src python3 -m alga.driver examples/01_validos/05_demo.alga
```

Si no encuentra errores, muestra:

```text
OK: fase semantic; análisis estático completado
```

`PYTHONPATH=src` permite importar el paquete `alga`. El repositorio no incluye
`pyproject.toml` ni `setup.py`: instalar `requirements.txt` no instala el proyecto
como paquete. Ejecuta el CLI con `-m alga.driver`, como en los ejemplos.

### Fases y salida JSON

```bash
# Mostrar tokens, lexemas, líneas y columnas.
PYTHONPATH=src python3 -m alga.driver examples/01_validos/05_demo.alga --phase lex

# Mostrar el árbol sintáctico si no hay errores.
PYTHONPATH=src python3 -m alga.driver examples/01_validos/05_demo.alga --phase parse

# Comprobar también tipos, dimensiones y ámbitos (fase predeterminada).
PYTHONPATH=src python3 -m alga.driver examples/01_validos/05_demo.alga --phase semantic

# Obtener tokens, errores y árbol en JSON.
PYTHONPATH=src python3 -m alga.driver examples/01_validos/05_demo.alga --json

# Consultar las opciones.
PYTHONPATH=src python3 -m alga.driver --help
```

Las fases se ejecutan en orden: léxico → sintáctico → semántico. Si una fase
detecta errores, las siguientes no se ejecutan. `--json` se puede combinar con
cualquier `--phase`; `tree` es `null` cuando no se llega a construir el árbol.
Los archivos de entrada se leen como UTF-8.

Los diagnósticos indican `fase:línea:columna: mensaje`, con posiciones desde 1.
En modo texto van a la salida de error; con `--json`, se incluyen en `errors`
en la salida estándar. Un fallo al leer el archivo se informa por la salida de
error incluso con `--json`.

| Código de salida del CLI | Significado |
| --- | --- |
| `0` | La fase solicitada terminó sin errores. |
| `1` | Se encontraron errores en el programa Alga. |
| `2` | Argumentos incorrectos o archivo de entrada ilegible/inexistente. |

### Ejemplos y particularidades del lenguaje

- `examples/01_validos/`: programas que deben superar el análisis completo.
- `examples/02_errores_lexicos/`, `03_errores_sintacticos/` y
  `04_errores_semanticos/`: casos que fallan intencionalmente.
- `examples/05_metodos_numericos/`: Jacobi, Gauss-Jordan y LU expresados en Alga.
  Consulta su [README](examples/05_metodos_numericos/README.md) para conocer los
  supuestos de los algoritmos; el analizador no calcula sus resultados.
- `examples/casos.json`: manifiesto con la fase y el resultado esperado por caso.

Ejemplo de validación de un método numérico:

```bash
PYTHONPATH=src python3 -m alga.driver examples/05_metodos_numericos/01_jacobi.alga
```

Las declaraciones, asignaciones y expresiones terminan en `;`. Los bloques de
`if`, `else`, `while` y `for` requieren llaves. El contador de un `for` debe
declararse antes: la cabecera admite asignaciones, no declaraciones ni `i++`.
Las comparaciones disponibles son `==`, `!=`, `<` y `>`; no se admiten `<=`,
`>=` ni comparaciones encadenadas. El lexer actual no admite comentarios.

Las dimensiones deben ser enteros positivos. Los índices empiezan en cero;
los vectores requieren un índice y las matrices dos. Se verifican el tipo de
los índices y los límites de índices literales, pero no los valores de
expresiones dinámicas. Tampoco se comprueban la convergencia de los bucles,
divisiones por cero ni resultados numéricos.

## Pruebas y documentación de la gramática

Después de instalar las dependencias y generar los analizadores:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/derivations.py --check
```

Las pruebas usan `unittest`, incluido en Python; no requieren `pytest`.
Comprueban reglas de tipos, casos del manifiesto, el CLI y la gramática
documental. Los casos negativos pasan la prueba cuando se detecta el error
esperado.

Sin Java, JAR ni runtime de ANTLR puedes comprobar únicamente los tipos y la
documentación con:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_types.py' -v
python3 -m unittest discover -s tests -p 'test_glc.py' -v
python3 scripts/derivations.py --check
```

Para regenerar las 24 derivaciones de `docs/04_derivaciones/`:

```bash
python3 scripts/derivations.py
```

Este último comando sobrescribe los Markdown de derivaciones usando
`docs/glc.json` y `docs/ejemplos_informe.json`. Su verificador documental es
independiente del parser ANTLR y no sustituye las pruebas de integración.

## Estructura y scripts auxiliares

| Ruta | Contenido |
| --- | --- |
| `grammar/` | Gramáticas ANTLR del lexer y parser. |
| `src/alga/driver.py` | CLI y coordinación de las fases. |
| `src/alga/semantic.py` | Visitor semántico y ámbitos de variables. |
| `src/alga/types.py` | Tipos, operaciones, funciones e indexación. |
| `src/alga/generated/` | Código creado por `scripts/generate.py`. |
| `tests/` | Pruebas unitarias, documentales y de integración. |
| `docs/` | GLC, ejemplos del informe y derivaciones. |
| `examples/` | Programas válidos y casos de error. |
| `tools/` | Ubicación predeterminada del JAR, que se descarga por separado. |

Los siguientes scripts son auxiliares de entrega y **no son necesarios para
analizar programas**. En el estado actual del repositorio faltan entradas que
necesitan para funcionar:

- `python3 scripts/presentation.py`: necesita
  `entregables/09_presentacion.json` y escribe
  `entregables/09_presentacion.pdf`. No requiere paquetes Python adicionales.
- `python3 scripts/guide_pdf.py`: necesita
  `docs/12_cambios_docx_iteraciones.md`, la carpeta `entregables/` y las
  bibliotecas del sistema Cairo, Pango, Pangocairo y GObject. Escribe
  `entregables/12_cambios_docx_iteraciones.pdf`.
- `python3 scripts/package.py`: intenta crear `dist/alga_hito1.zip`, pero exige
  archivos de raíz que no están incluidos: `.gitignore`,
  `Teoria_de_Compiladores_Trabajo_Parcial_y_Final.pdf` y
  `Grupo 2 Trabajo Parcial Compiladores(1).docx`. Hasta restaurarlos o adaptar
  su lista `ROOT_FILES`, falla. El ZIP excluye el código `generated`, los
  entornos virtuales y el JAR de `tools/`; quien lo reciba deberá preparar
  ANTLR y generar los analizadores nuevamente.

Las derivaciones también contienen una referencia a `docs/03_gramatica.md`,
ausente en esta copia; la GLC disponible está en `docs/glc.json`.

## Problemas frecuentes

| Mensaje o problema | Solución |
| --- | --- |
| `Se requiere Java y ANTLR 4.13.2` | Verifica `java -version`, el JAR en `tools/` y cualquier valor de `ANTLR_JAR`. |
| `No module named antlr4` | Activa `.venv` e instala `requirements.txt` con el mismo intérprete que ejecutará el CLI. |
| `No module named alga` | Ejecuta desde la raíz con `PYTHONPATH=src`. |
| `No module named alga.generated` | Ejecuta `python3 scripts/generate.py` antes del CLI y de las pruebas de integración. |
| Error de versión entre ANTLR y el runtime | Usa el JAR 4.13.2, reinstala los requisitos y regenera los analizadores. |
| `externally-managed-environment` al instalar con pip | Crea y activa `.venv` antes de instalar las dependencias. |
| No se puede crear `.venv` o falta `ensurepip` | Instala el soporte `venv` correspondiente a tu Python según tu distribución. |
| El programa muestra `OK` pero no imprime cálculos | Es el comportamiento esperado: esta entrega solo realiza análisis estático. |

En una nueva terminal, vuelve a ejecutar `source .venv/bin/activate` y conserva
`PYTHONPATH=src` en los comandos. Para salir del entorno virtual, usa `deactivate`.
