.data
    A : matrix[2][2]  ; 32 bytes
    b : vector[2]     ; 16 bytes
    x : vector[2]     ; 16 bytes
    d : scalar        ; 8 bytes
    r : vector[2]     ; 16 bytes
    t2 : vector[2]    ; 16 bytes
    t3 : vector[2]    ; 16 bytes
    t4 : vector[2]    ; 16 bytes
.code
    A[0] = 4
    A[8] = 1
    A[16] = 2
    A[24] = 3
    b[0] = 1
    b[8] = 2
    param A
    t1 = call det, 1
    d = t1
    param A
    param b
    t2 = call solve, 2
    x = t2
    t3 = A * x
    t4 = b - t3
    r = t4
    param r
    t5 = call norm, 1
    param t5
    call print, 1
