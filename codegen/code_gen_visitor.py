from decimal import Decimal

from gen.AlgaParser import AlgaParser
from gen.AlgaParserVisitor import AlgaParserVisitor
from semantic.type_rules import BOOL, SCALAR, VOID, Type, binary, builtin

from .TACEmitter import WORD, TACEmitter, is_number


class CodeGenVisitor(AlgaParserVisitor):
    def __init__(self, semantic):
        self.semantic = semantic
        self.tac = TACEmitter()

    # S → L
    def visitS(self, ctx):
        self.visit(ctx.l())

    # L → stmt L | ε
    def visitL(self, ctx):
        while ctx.stmt() is not None:
            self.visit(ctx.stmt())
            ctx = ctx.l()

    # B → { L }
    def visitB(self, ctx):
        self.visit(ctx.l())

    # D → scalar id J ; | vector id [ num ] J ; | matrix id [ num ] [ num ] J ;
    def visitD(self, ctx):
        symbol = self.semantic.decls[ctx]
        name = symbol.unique
        self.tac.declare(name, symbol.type_)

        initial = ctx.j().e()
        if initial is None:
            return
        self._assign_to_variable(name, initial)

    # A → As ;
    def visitA(self, ctx):
        self.visit(ctx.asig())

    # As → Ref = E
    def visitAsig(self, ctx):
        target = ctx.ref()
        symbol = self.semantic.refs[target]
        suffix = target.u()

        if suffix.e() is None:
            # ? x = E
            self._assign_to_variable(symbol.unique, ctx.e())
            return

        move = self._move(symbol, suffix)
        value = self.visit(ctx.e())
        self.tac.emit_store(symbol.unique, move, value)

    def _assign_to_variable(self, nombre, expr):
        literal = self._literal_like(expr)
        if literal is not None:
            self._fill_literal(nombre, literal)
        else:
            self.tac.emit_copy(nombre, self.visit(expr))

    # Ref → id U
    def visitRef(self, ctx):
        symbol = self.semantic.refs[ctx]
        suffix = ctx.u()
        if suffix.e() is None:
            return symbol.unique
        move = self._move(symbol, suffix)
        target = self.tac.new_temp(SCALAR)
        self.tac.emit_load(target, symbol.unique, move)
        return target

    def _move(self, simbolo, suffix):
        idxs = [self.visit(suffix.e())]
        if suffix.u1().e() is not None:
            idxs.append(self.visit(suffix.u1().e()))

        if len(idxs) == 1:
            lineal = idxs[0]
        else:
            columns = simbolo.type_.shape[1]
            row = self._arithm("*", idxs[0], str(columns))
            lineal = self._arithm("+", row, idxs[1])
        return self._arithm("*", lineal, str(WORD))

    @staticmethod
    def _int(text):
        if not is_number(text):
            return None
        value = Decimal(text)
        return int(value) if value == value.to_integral_value() else None

    def _arithm(self, op, left, right):
        a, b = self._int(left), self._int(right)
        if a is not None and b is not None:
            return str(a + b if op == "+" else a * b)
        # Elemento neutro: 0 + x = x, 1 * x = x
        neutral = 0 if op == "+" else 1
        if a == neutral:
            return right
        if b == neutral:
            return left
        target = self.tac.new_temp(SCALAR)
        self.tac.emit(target, left, op, right)
        return target

    def visitExprstmt(self, ctx):
        return self.visit(ctx.e())

    # E → T E′
    def visitE(self, ctx):
        result = self.visit(ctx.t())
        tail = ctx.eprima()
        while tail.t() is not None:
            right = self.visit(tail.t())
            result = self._op(tail.start.text, result, right)
            tail = tail.eprima()
        return result

    # T → F T′
    def visitT(self, ctx):
        result = self.visit(ctx.f())
        tail = ctx.tprima()
        while tail.f() is not None:
            right = self.visit(tail.f())
            result = self._op(tail.start.text, result, right)
            tail = tail.tprima()
        return result

    def _op(self, op, izq, der):
        tipo = binary(op, self.tac.type_of(izq), self.tac.type_of(der))
        destino = self.tac.new_temp(tipo)
        self.tac.emit(destino, izq, op, der)
        return destino

    # F → + F | - F | num | string | Ref | ( E ) | V | M | H ( E K )
    def visitF(self, ctx):
        if ctx.h() is not None:
            return self._call(ctx)
        if ctx.f() is not None:
            operand = self.visit(ctx.f())
            if ctx.start.text == "+":
                return operand
            if is_number(operand):
                return operand[1:] if operand.startswith("-") else "-" + operand
            target = self.tac.new_temp(self.tac.type_of(operand))
            self.tac.emit_neg(target, operand)
            return target
        if ctx.NUM() is not None:
            return ctx.NUM().getText()
        if ctx.STRING() is not None:
            return ctx.STRING().getText()
        if ctx.ref() is not None:
            return self.visit(ctx.ref())
        if ctx.e() is not None:
            return self.visit(ctx.e())

        literal = ctx.v() if ctx.v() is not None else ctx.m()
        temp = self.tac.new_temp(self._literal_type(literal))
        self._fill_literal(temp, literal)
        return temp

    def _call(self, ctx):
        name = ctx.h().getText()
        arguments = [self.visit(ctx.e())]
        tail = ctx.k()
        while tail.e() is not None:
            arguments.append(self.visit(tail.e()))
            tail = tail.k()

        type = builtin(name, [self.tac.type_of(a) for a in arguments])
        for argument in arguments:
            self.tac.emit_param(argument)
        if type == VOID:
            self.tac.emit_call(name, len(arguments))
            return None
        target = self.tac.new_temp(type)
        self.tac.emit_call(name, len(arguments), target)
        return target

    @staticmethod
    def _literal_like(expr):
        if expr.eprima().t() is not None:
            return None
        term = expr.t()
        if term.tprima().f() is not None:
            return None
        factor = term.f()
        if factor.v() is not None:
            return factor.v()
        return factor.m()

    @staticmethod
    def _vector_values(v):
        items = [v.n()]
        tail = v.nprima()
        while tail.n() is not None:
            items.append(tail.n())
            tail = tail.nprima()
        values = []
        for n in items:
            signo = "-" if n.z().getText() == "-" else ""
            values.append(signo + n.NUM().getText())
        return values

    def _rows(self, literal):
        if isinstance(literal, AlgaParser.VContext):
            return [self._vector_values(literal)]
        rows = [self._vector_values(literal.v())]
        tail = literal.mprima()
        while tail.v() is not None:
            rows.append(self._vector_values(tail.v()))
            tail = tail.mprima()
        return rows

    def _literal_type(self, literal):
        rows = self._rows(literal)
        if isinstance(literal, AlgaParser.VContext):
            return Type("vector", (len(rows[0]),))
        return Type("matrix", (len(rows), len(rows[0])))

    def _fill_literal(self, name, literal):
        position = 0
        for fila in self._rows(literal):
            for value in fila:
                self.tac.emit_store(name, str(position * WORD), value)
                position += 1

    # C → E Q   Q → R E | ε
    def visitC(self, ctx):
        left = self.visit(ctx.e())
        tail = ctx.q()
        if tail.e() is None:
            return left
        right = self.visit(tail.e())
        target = self.tac.new_temp(BOOL)
        self.tac.emit(target, left, tail.r().getText(), right)
        return target

    # I → if ( C ) B O   O → else B | ε
    def visitI(self, ctx):
        condition = self.visit(ctx.c())
        else_block = ctx.o().b()
        else_tag = self.tac.new_tag()
        end_Tag = self.tac.new_tag() if else_block is not None else else_tag

        self.tac.emit_goto_false(condition, else_tag)
        self.visit(ctx.b())
        if else_block is not None:
            self.tac.emit_goto(end_Tag)
            self.tac.emit_Tag(else_tag)
            self.visit(else_block)
        self.tac.emit_Tag(end_Tag)

    # W → while ( C ) B | for ( As ; C ; As ) B
    def visitW(self, ctx):
        assigns = ctx.asig()
        if assigns:
            self.visit(assigns[0])

        start = self.tac.new_tag()
        end = self.tac.new_tag()
        self.tac.emit_Tag(start)
        condition = self.visit(ctx.c())
        self.tac.emit_goto_false(condition, end)
        self.visit(ctx.b())
        if assigns:
            self.visit(assigns[1])
        self.tac.emit_goto(start)
        self.tac.emit_Tag(end)
