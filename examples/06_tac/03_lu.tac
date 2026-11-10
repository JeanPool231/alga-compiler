.data
    A : matrix[2][2]  ; 32 bytes
    L : matrix[2][2]  ; 32 bytes
    U : matrix[2][2]  ; 32 bytes
    i : scalar        ; 8 bytes
    j : scalar        ; 8 bytes
    k : scalar        ; 8 bytes
    valido : scalar   ; 8 bytes
.code
    A[0] = 4
    A[8] = 3
    A[16] = 6
    A[24] = 3
    L[0] = 1
    L[8] = 0
    L[16] = 0
    L[24] = 1
    U = A
    valido = 1
    k = 0
L1:
    t1 = k < 2
    ifFalse t1 goto L2
    t2 = valido == 1
    ifFalse t2 goto L3
    t3 = k * 2
    t4 = t3 + k
    t5 = t4 * 8
    t6 = U[t5]
    t7 = t6 != 0
    ifFalse t7 goto L4
    t8 = k + 1
    i = t8
L6:
    t9 = i < 2
    ifFalse t9 goto L7
    t10 = i * 2
    t11 = t10 + k
    t12 = t11 * 8
    t13 = i * 2
    t14 = t13 + k
    t15 = t14 * 8
    t16 = U[t15]
    t17 = k * 2
    t18 = t17 + k
    t19 = t18 * 8
    t20 = U[t19]
    t21 = t16 / t20
    L[t12] = t21
    j = k
L8:
    t22 = j < 2
    ifFalse t22 goto L9
    t23 = i * 2
    t24 = t23 + j
    t25 = t24 * 8
    t26 = i * 2
    t27 = t26 + j
    t28 = t27 * 8
    t29 = U[t28]
    t30 = i * 2
    t31 = t30 + k
    t32 = t31 * 8
    t33 = L[t32]
    t34 = k * 2
    t35 = t34 + j
    t36 = t35 * 8
    t37 = U[t36]
    t38 = t33 * t37
    t39 = t29 - t38
    U[t25] = t39
    t40 = j + 1
    j = t40
    goto L8
L9:
    t41 = i + 1
    i = t41
    goto L6
L7:
    goto L5
L4:
    valido = 0
L5:
L3:
    t42 = k + 1
    k = t42
    goto L1
L2:
    t43 = valido == 1
    ifFalse t43 goto L10
    param L
    call print, 1
    param U
    call print, 1
    goto L11
L10:
    param "LU sin pivoteo no aplicable"
    call print, 1
L11:
