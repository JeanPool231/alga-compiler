_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def decode_string(literal):
    body = literal[1:-1]
    out, idx = [], 0
    
    while idx < len(body):
        char = body[idx]
        
        if char == "\\" and idx + 1 < len(body):
            out.append(_ESCAPES.get(body[idx + 1], "\\" + body[idx + 1]))
            idx += 2
        else:
            out.append(char)
            idx += 1
            
    return "".join(out)


def string_literal(expr):
    if expr.eprima().t() is not None:
        return None
    
    term = expr.t()
    if term.tprima().f() is not None:
        return None
    
    factor = term.f()
    if factor.STRING() is None:
        return None
    
    return factor.STRING().getText()
