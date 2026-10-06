# Asignaciones: cuatro derivaciones más a la izquierda

GLC ampliada propuesta para el informe (ver `../03_gramatica.md`). `id`, `num` y `string` son terminales; sus lexemas se indican debajo. Cada fila sustituye un solo no terminal, siempre el situado más a la izquierda. La derivación parte del no terminal de la construcción; desde S se alcanza con `S ⇒ L ⇒ stmt L ⇒ A L` y al final `L ⇒ ε`.

## Ejemplo 1

```alga
k = 5.5;
```

Lexemas en orden: `id=k num=5.5`

```text
00. A    [Inicio]
01. As ;    [A → As ;]
02. Ref = E ;    [As → Ref = E]
03. id U = E ;    [Ref → id U]
04. id = E ;    [U → ε]
05. id = T E′ ;    [E → T E′]
06. id = F T′ E′ ;    [T → F T′]
07. id = num T′ E′ ;    [F → num]
08. id = num E′ ;    [T′ → ε]
09. id = num ;    [E′ → ε]
```

## Ejemplo 2

```alga
A = [[1,2],[3,4]];
```

Lexemas en orden: `id=A num=1 num=2 num=3 num=4`

```text
00. A    [Inicio]
01. As ;    [A → As ;]
02. Ref = E ;    [As → Ref = E]
03. id U = E ;    [Ref → id U]
04. id = E ;    [U → ε]
05. id = T E′ ;    [E → T E′]
06. id = F T′ E′ ;    [T → F T′]
07. id = M T′ E′ ;    [F → M]
08. id = [ V M′ ] T′ E′ ;    [M → [ V M′ ]]
09. id = [ [ N N′ ] M′ ] T′ E′ ;    [V → [ N N′ ]]
10. id = [ [ Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
11. id = [ [ num N′ ] M′ ] T′ E′ ;    [Z → ε]
12. id = [ [ num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
13. id = [ [ num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
14. id = [ [ num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
15. id = [ [ num , num ] M′ ] T′ E′ ;    [N′ → ε]
16. id = [ [ num , num ] , V M′ ] T′ E′ ;    [M′ → , V M′]
17. id = [ [ num , num ] , [ N N′ ] M′ ] T′ E′ ;    [V → [ N N′ ]]
18. id = [ [ num , num ] , [ Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
19. id = [ [ num , num ] , [ num N′ ] M′ ] T′ E′ ;    [Z → ε]
20. id = [ [ num , num ] , [ num , N N′ ] M′ ] T′ E′ ;    [N′ → , N N′]
21. id = [ [ num , num ] , [ num , Z num N′ ] M′ ] T′ E′ ;    [N → Z num]
22. id = [ [ num , num ] , [ num , num N′ ] M′ ] T′ E′ ;    [Z → ε]
23. id = [ [ num , num ] , [ num , num ] M′ ] T′ E′ ;    [N′ → ε]
24. id = [ [ num , num ] , [ num , num ] ] T′ E′ ;    [M′ → ε]
25. id = [ [ num , num ] , [ num , num ] ] E′ ;    [T′ → ε]
26. id = [ [ num , num ] , [ num , num ] ] ;    [E′ → ε]
```

## Ejemplo 3

```alga
C = A * B;
```

Lexemas en orden: `id=C id=A id=B`

```text
00. A    [Inicio]
01. As ;    [A → As ;]
02. Ref = E ;    [As → Ref = E]
03. id U = E ;    [Ref → id U]
04. id = E ;    [U → ε]
05. id = T E′ ;    [E → T E′]
06. id = F T′ E′ ;    [T → F T′]
07. id = Ref T′ E′ ;    [F → Ref]
08. id = id U T′ E′ ;    [Ref → id U]
09. id = id T′ E′ ;    [U → ε]
10. id = id * F T′ E′ ;    [T′ → * F T′]
11. id = id * Ref T′ E′ ;    [F → Ref]
12. id = id * id U T′ E′ ;    [Ref → id U]
13. id = id * id T′ E′ ;    [U → ε]
14. id = id * id E′ ;    [T′ → ε]
15. id = id * id ;    [E′ → ε]
```

## Ejemplo 4

```alga
v = u + [2,2,2];
```

Lexemas en orden: `id=v id=u num=2 num=2 num=2`

```text
00. A    [Inicio]
01. As ;    [A → As ;]
02. Ref = E ;    [As → Ref = E]
03. id U = E ;    [Ref → id U]
04. id = E ;    [U → ε]
05. id = T E′ ;    [E → T E′]
06. id = F T′ E′ ;    [T → F T′]
07. id = Ref T′ E′ ;    [F → Ref]
08. id = id U T′ E′ ;    [Ref → id U]
09. id = id T′ E′ ;    [U → ε]
10. id = id E′ ;    [T′ → ε]
11. id = id + T E′ ;    [E′ → + T E′]
12. id = id + F T′ E′ ;    [T → F T′]
13. id = id + V T′ E′ ;    [F → V]
14. id = id + [ N N′ ] T′ E′ ;    [V → [ N N′ ]]
15. id = id + [ Z num N′ ] T′ E′ ;    [N → Z num]
16. id = id + [ num N′ ] T′ E′ ;    [Z → ε]
17. id = id + [ num , N N′ ] T′ E′ ;    [N′ → , N N′]
18. id = id + [ num , Z num N′ ] T′ E′ ;    [N → Z num]
19. id = id + [ num , num N′ ] T′ E′ ;    [Z → ε]
20. id = id + [ num , num , N N′ ] T′ E′ ;    [N′ → , N N′]
21. id = id + [ num , num , Z num N′ ] T′ E′ ;    [N → Z num]
22. id = id + [ num , num , num N′ ] T′ E′ ;    [Z → ε]
23. id = id + [ num , num , num ] T′ E′ ;    [N′ → ε]
24. id = id + [ num , num , num ] E′ ;    [T′ → ε]
25. id = id + [ num , num , num ] ;    [E′ → ε]
```
