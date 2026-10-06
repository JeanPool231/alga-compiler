# Gramática del informe y correspondencia con ANTLR

La fuente es `Grupo 2 Trabajo Parcial Compiladores.docx`, sección 5.
Las reglas se conservan una a una en `grammar/AlgaParser.g4`.
ANTLR requiere nombres de parser en minúscula; los nombres en mayúscula
se reservan para tokens. Las primas se escriben `prima` y `As` se llama
`asig` para no colisionar con la palabra reservada `as` de Python.

| DOCX | Regla ANTLR |
| --- | --- |
| `S` | `s` |
| `L` | `l` |
| `stmt` | `stmt` |
| `D` | `d` |
| `J` | `j` |
| `A` | `a` |
| `As` | `asig` |
| `Ref` | `ref` |
| `U` | `u` |
| `U1` | `u1` |
| `exprstmt` | `exprstmt` |
| `E` | `e` |
| `E′` | `eprima` |
| `T` | `t` |
| `T′` | `tprima` |
| `F` | `f` |
| `H` | `h` |
| `K` | `k` |
| `V` | `v` |
| `N′` | `nprima` |
| `N` | `n` |
| `Z` | `z` |
| `M` | `m` |
| `M′` | `mprima` |
| `I` | `i` |
| `O` | `o` |
| `B` | `b` |
| `C` | `c` |
| `Q` | `q` |
| `R` | `r` |
| `W` | `w` |

## Producciones

```text
S → L
L → stmt L | ε
stmt → D | A | exprstmt | I | W
D → scalar id J ; | vector id [ num ] J ; | matrix id [ num ] [ num ] J ;
J → = E | ε
A → As ;
As → Ref = E
Ref → id U
U → [ E ] U1 | ε
U1 → [ E ] | ε
exprstmt → E ;
E → T E′
E′ → + T E′ | - T E′ | ε
T → F T′
T′ → * F T′ | / F T′ | ε
F → + F | - F | num | string | Ref | ( E ) | V | M | H ( E K )
H → id | transpose | det | trace
K → , E K | ε
V → [ N N′ ]
N′ → , N N′ | ε
N → Z num
Z → + | - | ε
M → [ V M′ ]
M′ → , V M′ | ε
I → if ( C ) B O
O → else B | ε
B → { L }
C → E Q
Q → R E | ε
R → == | != | < | >
W → while ( C ) B | for ( As ; C ; As ) B
```

## Adaptaciones de notación

- `id`, `num` y `string` se escriben `ID`, `NUM` y `STRING` en el G4.
- Los terminales literales se escriben con sus tokens `TK_*` del léxico.
- ε corresponde a una alternativa vacía (`| ;`).
- `s : l EOF ;` agrega el marcador de fin de archivo. No cambia las cadenas
  completas de la GLC; impide aceptar una entrada solo parcialmente.

La separación E/T/F conserva la precedencia. El visitor acumula las colas
E′ y T′ de izquierda a derecha para mantener la asociatividad de las operaciones.

## Derivaciones y comprobación

Las 24 derivaciones de [04_derivaciones](04_derivaciones/) parten del no terminal
de su construcción. Cada documento explica cómo llegar desde S. Los pasos
se obtienen del árbol ANTLR, se contrastan con `glc.json` y terminan en la
secuencia original de tokens. Ya no hay un parser documental independiente.

```bash
python3 scripts/derivations.py --check
python3 -m unittest discover -s tests -p test_consistency.py -v
```

Las pruebas comparan las producciones del DOCX y del G4 con `glc.json`.
También comprueban los cinco ejemplos de cada una de las cinco construcciones
del informe. Son comprobaciones sobre estas reglas y entradas, no una prueba
general de ausencia de ambigüedad.
