.data
    x : scalar  ; 8 bytes
    y : scalar  ; 8 bytes
    z : scalar  ; 8 bytes
    w : scalar  ; 8 bytes
    n : scalar  ; 8 bytes
    r : scalar  ; 8 bytes
.code
    x = 5
    y = 3
    t1 = y * 2
    t2 = x + t1
    z = t2
    t3 = x + y
    t4 = t3 * 2
    w = t4
    t5 = -x
    n = t5
    t6 = x - y
    t7 = t6 - 1
    r = t7
    param z
    call print, 1
