# Algoritmos numéricos expresados en Alga

Estos programas ilustran la ampliación del lenguaje. El front-end verifica su
estructura y tipos; **no los ejecuta**. Los siguientes resultados son referencias
matemáticas, no salidas obtenidas por el compilador.

| Archivo | Datos | Referencia |
|---|---|---|
| `01_jacobi.alga` | A = [[4,1],[2,3]], b = [1,2] | x = [0.1,0.6]; parada por residuo < 0.000001 o 100 iteraciones |
| `02_gauss_jordan.alga` | A aumentada = [[2,1,5],[1,-1,1]] | Filas finales [[1,0,2],[0,1,1]], solución [2,1] |
| `03_lu.alga` | A = [[4,3],[6,3]] | L = [[1,0],[1.5,1]], U = [[4,3],[0,-1.5]]; A = L*U |

Jacobi lee únicamente `x` durante cada barrido y escribe `nuevo`; la asignación
`x = nuevo` tiene semántica por valor. Es necesario conservar las componentes
anteriores hasta finalizar el barrido; véase [Netlib: Jacobi](https://netlib.org/linalg/html_templates/node12.html).
El ejemplo usa una diagonal no nula y no promete convergencia para cualquier matriz.

Gauss-Jordan y LU no incluyen pivoteo: ante un pivote cero desactivan el cálculo y
reportan esa limitación. Un pivote pequeño también puede perjudicar la estabilidad.
Para una implementación general hay que incorporar intercambio de filas y
criterios numéricos; véase [NIST DLMF 3.2(i)](https://dlmf.nist.gov/3.2#i).
Se guarda el pivote/factor antes de modificar las filas para no sobrescribirlo.

La comprobación documental acepta los tres programas. Su validación mediante el
pipeline ANTLR está preparada en `tests/test_pipeline.py` y el manifiesto de casos,
pero pendiente de dependencias. Ningún test actual certifica ejecución numérica.
