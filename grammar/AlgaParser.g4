parser grammar AlgaParser;
options { tokenVocab=AlgaLexer; }

// GLC ampliada: iteraciones y referencias indexadas; EOF obliga a consumir toda la entrada.
program: statementList EOF;
statementList: statement statementList | ;
statement: declaration | assignment | expressionStatement | conditional | iteration;
declaration
    : TK_SCALAR ID initializer TK_SEMICOLON
    | TK_VECTOR ID TK_LBRACKET NUM TK_RBRACKET initializer TK_SEMICOLON
    | TK_MATRIX ID TK_LBRACKET NUM TK_RBRACKET TK_LBRACKET NUM TK_RBRACKET initializer TK_SEMICOLON
    ;
initializer: TK_ASSIGN expression | ;
assignment: assignmentCore TK_SEMICOLON;
assignmentCore: reference TK_ASSIGN expression;
reference: ID indexSuffix;
indexSuffix: TK_LBRACKET expression TK_RBRACKET secondIndex | ;
secondIndex: TK_LBRACKET expression TK_RBRACKET | ;
iteration
    : TK_WHILE TK_LPAREN condition TK_RPAREN block
    | TK_FOR TK_LPAREN assignmentCore TK_SEMICOLON condition TK_SEMICOLON assignmentCore TK_RPAREN block
    ;
expressionStatement: expression TK_SEMICOLON;
expression: term expressionTail;
expressionTail: (TK_PLUS | TK_MINUS) term expressionTail | ;
term: factor termTail;
termTail: (TK_MULT | TK_DIV) factor termTail | ;
factor
    : (TK_PLUS | TK_MINUS) factor
    | NUM
    | STRING
    | reference
    | TK_LPAREN expression TK_RPAREN
    | vectorLiteral
    | matrixLiteral
    | functionName TK_LPAREN expression argumentsTail TK_RPAREN
    ;
functionName: ID | TK_TRANSPOSE | TK_DET | TK_TRACE;
argumentsTail: TK_COMMA expression argumentsTail | ;
vectorLiteral: TK_LBRACKET signedNumber numbersTail TK_RBRACKET;
numbersTail: TK_COMMA signedNumber numbersTail | ;
signedNumber: sign NUM;
sign: TK_PLUS | TK_MINUS | ;
matrixLiteral: TK_LBRACKET vectorLiteral rowsTail TK_RBRACKET;
rowsTail: TK_COMMA vectorLiteral rowsTail | ;
conditional: TK_IF TK_LPAREN condition TK_RPAREN block optionalElse;
optionalElse: TK_ELSE block | ;
block: TK_LBRACE statementList TK_RBRACE;
condition: expression comparisonTail;
comparisonTail: comparator expression | ;
comparator: TK_EQ | TK_NEQ | TK_LT | TK_GT;
