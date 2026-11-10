.data
    v : vector[3]     ; 24 bytes
    A : matrix[2][3]  ; 48 bytes
    i : scalar        ; 8 bytes
    j : scalar        ; 8 bytes
.code
    v[0] = 1
    v[8] = -2
    v[16] = 3
    A[0] = 1
    A[8] = 2
    A[16] = 3
    A[24] = 4
    A[32] = 5
    A[40] = 6
    i = 1
    j = 2
    A[40] = 7
    t1 = i * 8
    t2 = i * 3
    t3 = t2 + j
    t4 = t3 * 8
    t5 = A[t4]
    v[t1] = t5
