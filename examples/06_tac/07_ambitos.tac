.data
    k : scalar       ; 8 bytes
    k_1 : vector[2]  ; 16 bytes
.code
    k = 1
    t1 = k > 0
    ifFalse t1 goto L1
    k_1[0] = 5
    k_1[8] = 6
    k_1[0] = 9
L1:
    t2 = k + 1
    k = t2
