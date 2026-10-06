# Declaraciones: cuatro derivaciones más a la izquierda

GLC del informe (ver [correspondencia con ANTLR](../03_gramatica.md)). `id`, `num` y `string` son terminales; sus lexemas se indican debajo. Cada fila sustituye un solo no terminal, siempre el situado más a la izquierda. La derivación parte del no terminal de la construcción; desde S se alcanza con `S ⇒ L ⇒ stmt L ⇒ D L` y al final `L ⇒ ε`.

## Ejemplo 1

```text
scalar k;
```

Lexemas en orden: `id=k`

```text
00. D    [Inicio]
01. scalar id J ;    [D → scalar id J ;]
02. scalar id ;    [J → ε]
```

## Ejemplo 2

```text
vector v[3];
```

Lexemas en orden: `id=v num=3`

```text
00. D    [Inicio]
01. vector id [ num ] J ;    [D → vector id [ num ] J ;]
02. vector id [ num ] ;    [J → ε]
```

## Ejemplo 3

```text
matrix M[3][4] = [[1,2,3,4],[5,6,7,8],[9,10,11,12]];
```

Lexemas en orden: `id=M num=3 num=4 num=1 num=2 num=3 num=4 num=5 num=6 num=7 num=8 num=9 num=10 num=11 num=12`

```text
00. D    [Inicio]
01. matrix id [ num ] [ num ] J ;    [D → matrix id [ num ] [ num ] J ;]
02. matrix id [ num ] [ num ] = E ;    [J → = E]
03. matrix id [ num ] [ num ] = T E′ ;    [E → T E′]
04. matrix id [ num ] [ num ] = F T′ E′ ;    [T → F T′]
05. matrix id [ num ] [ num ] = M T′ E′ ;    [F → M]
06. matrix id [ num ] [ num ] = [ V M′ ] T′ E′ ;    [M → [ V M′ ]]
07. matrix id [ num ] [ num ] = [ [ N N′ ] M′ ] T′ E′ ;    [V → [ N N′ ]]
08. matrix id [ num ] [ num ] = [ [ Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
09. matrix id [ num ] [ num ] = [ [ num N′ ] M′ ] T′ E′ ;    [Z → ε]
10. matrix id [ num ] [ num ] = [ [ num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
11. matrix id [ num ] [ num ] = [ [ num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
12. matrix id [ num ] [ num ] = [ [ num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
13. matrix id [ num ] [ num ] = [ [ num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
14. matrix id [ num ] [ num ] = [ [ num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
15. matrix id [ num ] [ num ] = [ [ num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
16. matrix id [ num ] [ num ] = [ [ num , num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
17. matrix id [ num ] [ num ] = [ [ num , num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
18. matrix id [ num ] [ num ] = [ [ num , num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
19. matrix id [ num ] [ num ] = [ [ num , num , num , num ] M′ ] T′ E′ ;    [N′ → ε]
20. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , V M′ ] T′ E′ ;    [M′ → , V M′]
21. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ N N′ ] M′ ] T′ E′ ;    [V → [ N N′ ]]
22. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
23. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num N′ ] M′ ] T′ E′ ;    [Z → ε]
24. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
25. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
26. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
27. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
28. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
29. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
30. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
31. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
32. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
33. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] M′ ] T′ E′ ;    [N′ → ε]
34. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , V M′ ] T′ E′ ;    [M′ → , V M′]
35. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ N N′ ] M′ ] T′ E′ ;    [V → [ N N′ ]]
36. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
37. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num N′ ] M′ ] T′ E′ ;    [Z → ε]
38. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
39. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
40. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
41. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
42. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
43. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
44. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
45. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
46. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
47. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , num ] M′ ] T′ E′ ;    [N′ → ε]
48. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , num ] ] T′ E′ ;    [M′ → ε]
49. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , num ] ] E′ ;    [T′ → ε]
50. matrix id [ num ] [ num ] = [ [ num , num , num , num ] , [ num , num , num , num ] , [ num , num , num , num ] ] ;    [E′ → ε]
```

## Ejemplo 4

```text
vector u[3] = [1.5,2.0,-3.5];
```

Lexemas en orden: `id=u num=3 num=1.5 num=2.0 num=3.5`

```text
00. D    [Inicio]
01. vector id [ num ] J ;    [D → vector id [ num ] J ;]
02. vector id [ num ] = E ;    [J → = E]
03. vector id [ num ] = T E′ ;    [E → T E′]
04. vector id [ num ] = F T′ E′ ;    [T → F T′]
05. vector id [ num ] = V T′ E′ ;    [F → V]
06. vector id [ num ] = [ N N′ ] T′ E′ ;    [V → [ N N′ ]]
07. vector id [ num ] = [ Z num N′ ] T′ E′ ;    [N → Z num]
08. vector id [ num ] = [ num N′ ] T′ E′ ;    [Z → ε]
09. vector id [ num ] = [ num , N N′ ] T′ E′ ;    [N′ → , N N′]
10. vector id [ num ] = [ num , Z num N′ ] T′ E′ ;    [N → Z num]
11. vector id [ num ] = [ num , num N′ ] T′ E′ ;    [Z → ε]
12. vector id [ num ] = [ num , num , N N′ ] T′ E′ ;    [N′ → , N N′]
13. vector id [ num ] = [ num , num , Z num N′ ] T′ E′ ;    [N → Z num]
14. vector id [ num ] = [ num , num , - num N′ ] T′ E′ ;    [Z → -]
15. vector id [ num ] = [ num , num , - num ] T′ E′ ;    [N′ → ε]
16. vector id [ num ] = [ num , num , - num ] E′ ;    [T′ → ε]
17. vector id [ num ] = [ num , num , - num ] ;    [E′ → ε]
```
