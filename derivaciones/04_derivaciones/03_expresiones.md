# Expresiones: cuatro derivaciones más a la izquierda

GLC del informe (ver [correspondencia con ANTLR](../03_gramatica.md)). `id`, `num` y `string` son terminales; sus lexemas se indican debajo. Cada fila sustituye un solo no terminal, siempre el situado más a la izquierda. La derivación parte del no terminal de la construcción; desde S se alcanza con `S ⇒ L ⇒ stmt L ⇒ exprstmt L` y al final `L ⇒ ε`.

## Ejemplo 1

```text
A + B * k;
```

Lexemas en orden: `id=A id=B id=k`

```text
00. exprstmt    [Inicio]
01. E ;    [exprstmt → E ;]
02. T E′ ;    [E → T E′]
03. F T′ E′ ;    [T → F T′]
04. Ref T′ E′ ;    [F → Ref]
05. id U T′ E′ ;    [Ref → id U]
06. id T′ E′ ;    [U → ε]
07. id E′ ;    [T′ → ε]
08. id + T E′ ;    [E′ → + T E′]
09. id + F T′ E′ ;    [T → F T′]
10. id + Ref T′ E′ ;    [F → Ref]
11. id + id U T′ E′ ;    [Ref → id U]
12. id + id T′ E′ ;    [U → ε]
13. id + id * F T′ E′ ;    [T′ → * F T′]
14. id + id * Ref T′ E′ ;    [F → Ref]
15. id + id * id U T′ E′ ;    [Ref → id U]
16. id + id * id T′ E′ ;    [U → ε]
17. id + id * id E′ ;    [T′ → ε]
18. id + id * id ;    [E′ → ε]
```

## Ejemplo 2

```text
transpose(A) * b;
```

Lexemas en orden: `id=A id=b`

```text
00. exprstmt    [Inicio]
01. E ;    [exprstmt → E ;]
02. T E′ ;    [E → T E′]
03. F T′ E′ ;    [T → F T′]
04. H ( E K ) T′ E′ ;    [F → H ( E K )]
05. transpose ( E K ) T′ E′ ;    [H → transpose]
06. transpose ( T E′ K ) T′ E′ ;    [E → T E′]
07. transpose ( F T′ E′ K ) T′ E′ ;    [T → F T′]
08. transpose ( Ref T′ E′ K ) T′ E′ ;    [F → Ref]
09. transpose ( id U T′ E′ K ) T′ E′ ;    [Ref → id U]
10. transpose ( id T′ E′ K ) T′ E′ ;    [U → ε]
11. transpose ( id E′ K ) T′ E′ ;    [T′ → ε]
12. transpose ( id K ) T′ E′ ;    [E′ → ε]
13. transpose ( id ) T′ E′ ;    [K → ε]
14. transpose ( id ) * F T′ E′ ;    [T′ → * F T′]
15. transpose ( id ) * Ref T′ E′ ;    [F → Ref]
16. transpose ( id ) * id U T′ E′ ;    [Ref → id U]
17. transpose ( id ) * id T′ E′ ;    [U → ε]
18. transpose ( id ) * id E′ ;    [T′ → ε]
19. transpose ( id ) * id ;    [E′ → ε]
```

## Ejemplo 3

```text
(A - B) * (b + c);
```

Lexemas en orden: `id=A id=B id=b id=c`

```text
00. exprstmt    [Inicio]
01. E ;    [exprstmt → E ;]
02. T E′ ;    [E → T E′]
03. F T′ E′ ;    [T → F T′]
04. ( E ) T′ E′ ;    [F → ( E )]
05. ( T E′ ) T′ E′ ;    [E → T E′]
06. ( F T′ E′ ) T′ E′ ;    [T → F T′]
07. ( Ref T′ E′ ) T′ E′ ;    [F → Ref]
08. ( id U T′ E′ ) T′ E′ ;    [Ref → id U]
09. ( id T′ E′ ) T′ E′ ;    [U → ε]
10. ( id E′ ) T′ E′ ;    [T′ → ε]
11. ( id - T E′ ) T′ E′ ;    [E′ → - T E′]
12. ( id - F T′ E′ ) T′ E′ ;    [T → F T′]
13. ( id - Ref T′ E′ ) T′ E′ ;    [F → Ref]
14. ( id - id U T′ E′ ) T′ E′ ;    [Ref → id U]
15. ( id - id T′ E′ ) T′ E′ ;    [U → ε]
16. ( id - id E′ ) T′ E′ ;    [T′ → ε]
17. ( id - id ) T′ E′ ;    [E′ → ε]
18. ( id - id ) * F T′ E′ ;    [T′ → * F T′]
19. ( id - id ) * ( E ) T′ E′ ;    [F → ( E )]
20. ( id - id ) * ( T E′ ) T′ E′ ;    [E → T E′]
21. ( id - id ) * ( F T′ E′ ) T′ E′ ;    [T → F T′]
22. ( id - id ) * ( Ref T′ E′ ) T′ E′ ;    [F → Ref]
23. ( id - id ) * ( id U T′ E′ ) T′ E′ ;    [Ref → id U]
24. ( id - id ) * ( id T′ E′ ) T′ E′ ;    [U → ε]
25. ( id - id ) * ( id E′ ) T′ E′ ;    [T′ → ε]
26. ( id - id ) * ( id + T E′ ) T′ E′ ;    [E′ → + T E′]
27. ( id - id ) * ( id + F T′ E′ ) T′ E′ ;    [T → F T′]
28. ( id - id ) * ( id + Ref T′ E′ ) T′ E′ ;    [F → Ref]
29. ( id - id ) * ( id + id U T′ E′ ) T′ E′ ;    [Ref → id U]
30. ( id - id ) * ( id + id T′ E′ ) T′ E′ ;    [U → ε]
31. ( id - id ) * ( id + id E′ ) T′ E′ ;    [T′ → ε]
32. ( id - id ) * ( id + id ) T′ E′ ;    [E′ → ε]
33. ( id - id ) * ( id + id ) E′ ;    [T′ → ε]
34. ( id - id ) * ( id + id ) ;    [E′ → ε]
```

## Ejemplo 4

```text
trace(A) + k / 2.0;
```

Lexemas en orden: `id=A id=k num=2.0`

```text
00. exprstmt    [Inicio]
01. E ;    [exprstmt → E ;]
02. T E′ ;    [E → T E′]
03. F T′ E′ ;    [T → F T′]
04. H ( E K ) T′ E′ ;    [F → H ( E K )]
05. trace ( E K ) T′ E′ ;    [H → trace]
06. trace ( T E′ K ) T′ E′ ;    [E → T E′]
07. trace ( F T′ E′ K ) T′ E′ ;    [T → F T′]
08. trace ( Ref T′ E′ K ) T′ E′ ;    [F → Ref]
09. trace ( id U T′ E′ K ) T′ E′ ;    [Ref → id U]
10. trace ( id T′ E′ K ) T′ E′ ;    [U → ε]
11. trace ( id E′ K ) T′ E′ ;    [T′ → ε]
12. trace ( id K ) T′ E′ ;    [E′ → ε]
13. trace ( id ) T′ E′ ;    [K → ε]
14. trace ( id ) E′ ;    [T′ → ε]
15. trace ( id ) + T E′ ;    [E′ → + T E′]
16. trace ( id ) + F T′ E′ ;    [T → F T′]
17. trace ( id ) + Ref T′ E′ ;    [F → Ref]
18. trace ( id ) + id U T′ E′ ;    [Ref → id U]
19. trace ( id ) + id T′ E′ ;    [U → ε]
20. trace ( id ) + id / F T′ E′ ;    [T′ → / F T′]
21. trace ( id ) + id / num T′ E′ ;    [F → num]
22. trace ( id ) + id / num E′ ;    [T′ → ε]
23. trace ( id ) + id / num ;    [E′ → ε]
```
