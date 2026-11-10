.data
    i : scalar      ; 8 bytes
    j : scalar      ; 8 bytes
    total : scalar  ; 8 bytes
.code
    total = 0
    i = 0
L1:
    t1 = i < 2
    ifFalse t1 goto L2
    j = 0
L3:
    t2 = j < 3
    ifFalse t2 goto L4
    t3 = total + 1
    total = t3
    t4 = j + 1
    j = t4
    goto L3
L4:
    t5 = i + 1
    i = t5
    goto L1
L2:
