.data
    A : matrix[2][2]   ; 32 bytes
    b : vector[2]      ; 16 bytes
    x : vector[2]      ; 16 bytes
    nuevo : vector[2]  ; 16 bytes
    i : scalar         ; 8 bytes
    j : scalar         ; 8 bytes
    suma : scalar      ; 8 bytes
    iter : scalar      ; 8 bytes
    maxIter : scalar   ; 8 bytes
    tol : scalar       ; 8 bytes
    error : scalar     ; 8 bytes
    seguir : scalar    ; 8 bytes
    t1 : vector[2]     ; 16 bytes
    t2 : vector[2]     ; 16 bytes
    t27 : vector[2]    ; 16 bytes
    t28 : vector[2]    ; 16 bytes
.code
    A[0] = 4
    A[8] = 1
    A[16] = 2
    A[24] = 3
    b[0] = 1
    b[8] = 2
    x[0] = 0
    x[8] = 0
    nuevo[0] = 0
    nuevo[8] = 0
    iter = 0
    maxIter = 100
    tol = 0.000001
    t1 = A * x
    t2 = b - t1
    param t2
    t3 = call norm, 1
    error = t3
    seguir = 1
L1:
    t4 = seguir != 0
    ifFalse t4 goto L2
    i = 0
L3:
    t5 = i < 2
    ifFalse t5 goto L4
    suma = 0
    j = 0
L5:
    t6 = j < 2
    ifFalse t6 goto L6
    t7 = i != j
    ifFalse t7 goto L7
    t8 = i * 2
    t9 = t8 + j
    t10 = t9 * 8
    t11 = A[t10]
    t12 = j * 8
    t13 = x[t12]
    t14 = t11 * t13
    t15 = suma + t14
    suma = t15
L7:
    t16 = j + 1
    j = t16
    goto L5
L6:
    t17 = i * 8
    t18 = i * 8
    t19 = b[t18]
    t20 = t19 - suma
    t21 = i * 2
    t22 = t21 + i
    t23 = t22 * 8
    t24 = A[t23]
    t25 = t20 / t24
    nuevo[t17] = t25
    t26 = i + 1
    i = t26
    goto L3
L4:
    x = nuevo
    t27 = A * x
    t28 = b - t27
    param t28
    t29 = call norm, 1
    error = t29
    t30 = iter + 1
    iter = t30
    t31 = error < tol
    ifFalse t31 goto L8
    seguir = 0
L8:
    t32 = iter == maxIter
    ifFalse t32 goto L9
    seguir = 0
L9:
    goto L1
L2:
    t33 = error < tol
    ifFalse t33 goto L10
    param x
    call print, 1
    goto L11
L10:
    param "No convergio en maxIter"
    call print, 1
L11:
