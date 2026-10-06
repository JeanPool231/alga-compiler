"""Visitor de ANTLR: tabla de símbolos por bloque y comprobación de tipos."""
from .generated.AlgaParserVisitor import AlgaParserVisitor
from .types import Type, SCALAR, STRING, BOOL, ERROR, NUMERIC, binary, builtin, indexed


class SemanticAnalyzer(AlgaParserVisitor):
    def __init__(self):
        self.scopes = [{}]
        self.errors = []

    def error(self, ctx, message):
        self.errors.append(f'semántico:{ctx.start.line}:{ctx.start.column + 1}: {message}')
        return ERROR

    def lookup(self, ctx, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return self.error(ctx, f'Variable {name} no declarada')

    def compatible(self, ctx, expected, actual):
        if ERROR not in (expected, actual) and expected != actual:
            self.error(ctx, f'Se esperaba {expected}; se obtuvo {actual}')

    def visitProgram(self, ctx):
        self.visit(ctx.statementList())
        return self.errors

    def visitStatementList(self, ctx):
        while ctx.statement() is not None:
            self.visit(ctx.statement())
            ctx = ctx.statementList()

    def visitDeclaration(self, ctx):
        name = ctx.ID().getText()
        sizes = [n.getText() for n in ctx.NUM()]
        valid = all(s.isdigit() and int(s) > 0 for s in sizes)
        if not valid:
            declared = self.error(ctx, 'Las dimensiones deben ser enteros positivos')
        else:
            declared = Type(ctx.start.text, tuple(map(int, sizes)))
        # El inicializador se resuelve antes de introducir el nuevo nombre.
        init = ctx.initializer().expression()
        actual = self.visit(init) if init is not None else None
        if name in self.scopes[-1]:
            self.error(ctx, f'Variable {name} ya declarada en este ámbito')
        else:
            self.scopes[-1][name] = declared
        if actual is not None:
            self.compatible(ctx, declared, actual)

    def visitAssignment(self, ctx):
        self.visit(ctx.assignmentCore())

    def visitAssignmentCore(self, ctx):
        target = self.visit(ctx.reference())
        self.compatible(ctx, target, self.visit(ctx.expression()))

    def visitReference(self, ctx):
        base = self.lookup(ctx, ctx.ID().getText())
        suffix = ctx.indexSuffix()
        if suffix.expression() is None:
            return base
        expressions = [suffix.expression()]
        if suffix.secondIndex().expression() is not None:
            expressions.append(suffix.secondIndex().expression())
        types = [self.visit(expr) for expr in expressions]
        try:
            return indexed(base, types, [expr.getText() for expr in expressions])
        except ValueError as exc:
            return self.error(ctx, str(exc))

    def visitIteration(self, ctx):
        # Se comprueba el cuerpo una vez; el front-end nunca ejecuta el bucle.
        assignments = ctx.assignmentCore()
        if assignments:
            self.visit(assignments[0])
        self.visit(ctx.condition())
        self.visit(ctx.block())
        # La actualización no puede ver declaraciones locales del cuerpo.
        if assignments:
            self.visit(assignments[1])

    def visitExpressionStatement(self, ctx):
        return self.visit(ctx.expression())

    def visitExpression(self, ctx):
        result = self.visit(ctx.term())
        tail = ctx.expressionTail()
        while tail.term() is not None:
            result = self.operation(tail, result, self.visit(tail.term()))
            tail = tail.expressionTail()
        return result

    def visitTerm(self, ctx):
        result = self.visit(ctx.factor())
        tail = ctx.termTail()
        while tail.factor() is not None:
            result = self.operation(tail, result, self.visit(tail.factor()))
            tail = tail.termTail()
        return result

    def operation(self, ctx, left, right):
        try:
            return binary(ctx.start.text, left, right)
        except ValueError as exc:
            return self.error(ctx, str(exc))

    def visitFactor(self, ctx):
        if ctx.functionName() is not None:
            args = [self.visit(ctx.expression())]
            tail = ctx.argumentsTail()
            while tail.expression() is not None:
                args.append(self.visit(tail.expression()))
                tail = tail.argumentsTail()
            try:
                return builtin(ctx.functionName().getText(), args)
            except ValueError as exc:
                return self.error(ctx, str(exc))
        if ctx.factor() is not None:
            value = self.visit(ctx.factor())
            if value != ERROR and value.kind not in NUMERIC:
                return self.error(ctx, f'Signo unario no definido para {value}')
            return value
        if ctx.NUM() is not None:
            return SCALAR
        if ctx.STRING() is not None:
            return STRING
        if ctx.reference() is not None:
            return self.visit(ctx.reference())
        for child in (ctx.expression(), ctx.vectorLiteral(), ctx.matrixLiteral()):
            if child is not None:
                return self.visit(child)
        raise AssertionError('Alternativa de factor no contemplada')

    def visitVectorLiteral(self, ctx):
        count = 1
        tail = ctx.numbersTail()
        while tail.signedNumber() is not None:
            count += 1
            tail = tail.numbersTail()
        return Type('vector', (count,))

    def visitMatrixLiteral(self, ctx):
        row_types = [self.visit(ctx.vectorLiteral())]
        tail = ctx.rowsTail()
        while tail.vectorLiteral() is not None:
            row_types.append(self.visit(tail.vectorLiteral()))
            tail = tail.rowsTail()
        if any(row != row_types[0] for row in row_types):
            return self.error(ctx, 'La matriz literal debe ser rectangular')
        return Type('matrix', (len(row_types), row_types[0].shape[0]))

    def visitConditional(self, ctx):
        self.visit(ctx.condition())
        self.visit(ctx.block())
        if ctx.optionalElse().block() is not None:
            self.visit(ctx.optionalElse().block())

    def visitBlock(self, ctx):
        self.scopes.append({})
        try:
            self.visit(ctx.statementList())
        finally:
            self.scopes.pop()

    def visitCondition(self, ctx):
        left = self.visit(ctx.expression())
        tail = ctx.comparisonTail()
        if tail.expression() is None:
            if left not in (BOOL, ERROR):
                self.error(ctx, f'La condición requiere bool; se obtuvo {left}')
            return
        right = self.visit(tail.expression())
        if ERROR not in (left, right) and (left != SCALAR or right != SCALAR):
            self.error(ctx, f'La comparación requiere escalares; recibió {left} y {right}')
