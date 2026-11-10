.data
    A : matrix[2][3]  ; 48 bytes
    i : scalar        ; 8 bytes
    j : scalar        ; 8 bytes
    k : scalar        ; 8 bytes
    pivote : scalar   ; 8 bytes
    factor : scalar   ; 8 bytes
    valido : scalar   ; 8 bytes
.code
    A[0] = 2
    A[8] = 1
    A[16] = 5
    A[24] = 1
    A[32] = -1
    A[40] = 1
    valido = 1
    k = 0
L1:
    t1 = k < 2
    ifFalse t1 goto L2
    t2 = valido == 1
    ifFalse t2 goto L3
    t3 = k * 3
    t4 = t3 + k
    t5 = t4 * 8
    t6 = A[t5]
    pivote = t6
    t7 = pivote != 0
    ifFalse t7 goto L4
    j = 0
L6:
    t8 = j < 3
    ifFalse t8 goto L7
    t9 = k * 3
    t10 = t9 + j
    t11 = t10 * 8
    t12 = k * 3
    t13 = t12 + j
    t14 = t13 * 8
    t15 = A[t14]
    t16 = t15 / pivote
    A[t11] = t16
    t17 = j + 1
    j = t17
    goto L6
L7:
    i = 0
L8:
    t18 = i < 2
    ifFalse t18 goto L9
    t19 = i != k
    ifFalse t19 goto L10
    t20 = i * 3
    t21 = t20 + k
    t22 = t21 * 8
    t23 = A[t22]
    factor = t23
    j = 0
L11:
    t24 = j < 3
    ifFalse t24 goto L12
    t25 = i * 3
    t26 = t25 + j
    t27 = t26 * 8
    t28 = i * 3
    t29 = t28 + j
    t30 = t29 * 8
    t31 = A[t30]
    t32 = k * 3
    t33 = t32 + j
    t34 = t33 * 8
    t35 = A[t34]
    t36 = factor * t35
    t37 = t31 - t36
    A[t27] = t37
    t38 = j + 1
    j = t38
    goto L11
L12:
L10:
    t39 = i + 1
    i = t39
    goto L8
L9:
    goto L5
L4:
    valido = 0
L5:
L3:
    t40 = k + 1
    k = t40
    goto L1
L2:
    t41 = valido == 1
    ifFalse t41 goto L13
    t42 = A[16]
    param t42
    call print, 1
    t43 = A[40]
    param t43
    call print, 1
    goto L14
L13:
    param "Pivote cero: este ejemplo requiere pivoteo"
    call print, 1
L14:
