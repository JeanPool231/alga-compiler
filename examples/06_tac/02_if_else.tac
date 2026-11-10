.data
    a : scalar  ; 8 bytes
    b : scalar  ; 8 bytes
    m : scalar  ; 8 bytes
.code
    a = 10
    b = 20
    t1 = a > b
    ifFalse t1 goto L1
    m = a
    goto L2
L1:
    m = b
L2:
    t2 = m != 0
    ifFalse t2 goto L3
    param m
    call print, 1
L3:
