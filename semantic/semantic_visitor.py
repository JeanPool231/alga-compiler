from gen.AlgaParserVisitor import AlgaParserVisitor
from .symbol_table import SymbolTable
from .errors import SemanticError
from .type_rules import Type, SCALAR, STRING, BOOL, ERROR, NUMERIC
from .type_rules import binary, builtin, indexed


class SemanticVisitor(AlgaParserVisitor):
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []

    def _error(self, message, ctx):
        error = SemanticError(message, ctx.start.line, ctx.start.column + 1)
        self.errors.append(error)
        return ERROR

    def _compatible(self, expected, actual, ctx):
        if expected == ERROR or actual == ERROR:
            return
        if expected != actual:
            self._error(f'Se esperaba {expected}; se obtuvo {actual}', ctx)

    def _operation(self, ctx, left, right):
        try:
            return binary(ctx.start.text, left, right)
        except ValueError as error:
            return self._error(str(error), ctx)

    # S → L
    def visitS(self, ctx):
        self.visit(ctx.l())

    # L → stmt L | ε
    def visitL(self, ctx):
        # Recorrer la lista evita añadir una llamada Python por sentencia.
        while ctx.stmt() is not None:
            self.visit(ctx.stmt())
            ctx = ctx.l()

    # D → scalar id J ; | vector id [ num ] J ; | matrix id [ num ] [ num ] J ;
    def visitD(self, ctx):
        name = ctx.ID().getText()
        sizes = []
        valid = True
        for token in ctx.NUM():
            text = token.getText()
            if not text.isdigit() or int(text) <= 0:
                valid = False
            else:
                sizes.append(int(text))

        if valid:
            declared = Type(ctx.start.text, tuple(sizes))
        else:
            declared = self._error('Las dimensiones deben ser enteros positivos', ctx)

        # J → = E | ε. El nombre nuevo aún no está visible en su inicializador.
        actual = None
        if ctx.j().e() is not None:
            actual = self.visit(ctx.j().e())
        try:
            self.symtab.declare(name, declared, ctx.start.line, ctx.start.column + 1)
        except SemanticError as error:
            self.errors.append(error)
        if actual is not None:
            self._compatible(declared, actual, ctx)

    # A → As ;
    def visitA(self, ctx):
        self.visit(ctx.asig())

    # As → Ref = E
    def visitAsig(self, ctx):
        target = self.visit(ctx.ref())
        actual = self.visit(ctx.e())
        self._compatible(target, actual, ctx)

    # Ref → id U
    def visitRef(self, ctx):
        name = ctx.ID().getText()
        symbol = self.symtab.lookup(name)
        if symbol is None:
            base = self._error(f'Variable {name} no declarada', ctx)
        else:
            base = symbol.type_

        suffix = ctx.u()
        if suffix.e() is None:
            return base
        expressions = [suffix.e()]
        if suffix.u1().e() is not None:
            expressions.append(suffix.u1().e())
        types = []
        texts = []
        for expression in expressions:
            types.append(self.visit(expression))
            texts.append(expression.getText())
        try:
            return indexed(base, types, texts)
        except ValueError as error:
            return self._error(str(error), ctx)

    def visitExprstmt(self, ctx):
        return self.visit(ctx.e())

    # E → T E′. Acumular de izquierda a derecha conserva la asociatividad.
    def visitE(self, ctx):
        result = self.visit(ctx.t())
        tail = ctx.eprima()
        while tail.t() is not None:
            right = self.visit(tail.t())
            result = self._operation(tail, result, right)
            tail = tail.eprima()
        return result

    # T → F T′
    def visitT(self, ctx):
        result = self.visit(ctx.f())
        tail = ctx.tprima()
        while tail.f() is not None:
            right = self.visit(tail.f())
            result = self._operation(tail, result, right)
            tail = tail.tprima()
        return result

    # F → + F | - F | num | string | Ref | ( E ) | V | M | H ( E K )
    def visitF(self, ctx):
        if ctx.h() is not None:
            name = ctx.h().getText()
            args = [self.visit(ctx.e())]
            tail = ctx.k()
            while tail.e() is not None:
                args.append(self.visit(tail.e()))
                tail = tail.k()
            try:
                return builtin(name, args)
            except ValueError as error:
                return self._error(str(error), ctx)
        if ctx.f() is not None:
            type_ = self.visit(ctx.f())
            if type_ != ERROR and type_.kind not in NUMERIC:
                return self._error(f'Signo unario no definido para {type_}', ctx)
            return type_
        if ctx.NUM() is not None:
            return SCALAR
        if ctx.STRING() is not None:
            return STRING
        if ctx.ref() is not None:
            return self.visit(ctx.ref())
        if ctx.e() is not None:
            return self.visit(ctx.e())
        if ctx.v() is not None:
            return self.visit(ctx.v())
        return self.visit(ctx.m())

    # V → [ N N′ ]
    def visitV(self, ctx):
        count = 1
        tail = ctx.nprima()
        while tail.n() is not None:
            count += 1
            tail = tail.nprima()
        return Type('vector', (count,))

    # M → [ V M′ ]
    def visitM(self, ctx):
        first = self.visit(ctx.v())
        rows = 1
        regular = True
        tail = ctx.mprima()
        while tail.v() is not None:
            if self.visit(tail.v()) != first:
                regular = False
            rows += 1
            tail = tail.mprima()
        if not regular:
            return self._error('La matriz literal debe ser rectangular', ctx)
        return Type('matrix', (rows, first.shape[0]))

    # I → if ( C ) B O
    def visitI(self, ctx):
        self.visit(ctx.c())
        self.visit(ctx.b())
        if ctx.o().b() is not None:
            self.visit(ctx.o().b())

    # B → { L }
    def visitB(self, ctx):
        self.symtab.enter_scope()
        self.visit(ctx.l())
        self.symtab.exit_scope()

    # C → E Q   Q → R E | ε
    def visitC(self, ctx):
        left = self.visit(ctx.e())
        tail = ctx.q()
        if tail.e() is None:
            if left != BOOL and left != ERROR:
                self._error(f'La condición requiere bool; se obtuvo {left}', ctx)
            return
        right = self.visit(tail.e())
        if left == ERROR or right == ERROR:
            return
        if left != SCALAR or right != SCALAR:
            self._error(f'La comparación requiere escalares; recibió {left} y {right}', ctx)

    # W → while ( C ) B | for ( As ; C ; As ) B
    def visitW(self, ctx):
        assignments = ctx.asig()
        if assignments:
            self.visit(assignments[0])
        self.visit(ctx.c())
        # Se visita el cuerpo una vez: no se ejecuta el bucle.
        self.visit(ctx.b())
        if assignments:
            # Ya se salió del bloque: la actualización no ve sus variables locales.
            self.visit(assignments[1])
