lexer grammar AlgaLexer;

TK_MATRIX    : 'matrix' ;
TK_VECTOR    : 'vector' ;
TK_SCALAR    : 'scalar' ;
TK_IF        : 'if' ;
TK_ELSE      : 'else' ;
TK_WHILE     : 'while' ;
TK_FOR       : 'for' ;
TK_TRANSPOSE : 'transpose' ;
TK_DET       : 'det' ;
TK_TRACE     : 'trace' ;

TK_ASSIGN    : '=' ;
TK_PLUS      : '+' ;
TK_MINUS     : '-' ;
TK_MULT      : '*' ;
TK_DIV       : '/' ;
TK_EQ        : '==' ;
TK_NEQ       : '!=' ;
TK_LT        : '<' ;
TK_GT        : '>' ;
TK_LPAREN    : '(' ;
TK_RPAREN    : ')' ;
TK_LBRACKET  : '[' ;
TK_RBRACKET  : ']' ;
TK_LBRACE    : '{' ;
TK_RBRACE    : '}' ;
TK_SEMICOLON : ';' ;
TK_COMMA     : ',' ;

ID  : [a-zA-Z_] [a-zA-Z0-9_]* ;
NUM : [0-9]+ ('.' [0-9]+)? ;

WS : [ \t\r\n]+ -> skip ;
STRING : '"' ('\\' ["\\nrt] | ~["\\\r\n])* '"' ;
