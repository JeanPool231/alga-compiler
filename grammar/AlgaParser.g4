parser grammar AlgaParser;
options { tokenVocab=AlgaLexer; }

// Reglas del DOCX: los no terminales se escriben en minúscula en ANTLR.
// E′, T′, N′ y M′ se llaman eprima, tprima, nprima y mprima.
// As se llama asig porque "as" es una palabra reservada de Python.

//ESTRUCTURA GENERAL
// S → L. EOF obliga a reconocer todo el archivo
s : l EOF ;
l : stmt l | ;
stmt : d | a | exprstmt | i | w ;

//DECLARACIONES
// D → scalar id J ; | vector id [ num ] J ; | matrix id [ num ] [ num ] J ;
d : TK_SCALAR ID j TK_SEMICOLON
  | TK_VECTOR ID TK_LBRACKET NUM TK_RBRACKET j TK_SEMICOLON
  | TK_MATRIX ID TK_LBRACKET NUM TK_RBRACKET TK_LBRACKET NUM TK_RBRACKET j TK_SEMICOLON
  ;
j : TK_ASSIGN e | ;

//ASIGNACIONES Y REFERENCIAS
// A → As ;   As → Ref = E
// Ref → id U   U → [ E ] U1 | ε   U1 → [ E ] | ε
a : asig TK_SEMICOLON ;
asig : ref TK_ASSIGN e ;
ref : ID u ;
u : TK_LBRACKET e TK_RBRACKET u1 | ;
u1 : TK_LBRACKET e TK_RBRACKET | ;

//EXPRESIONES
// E → T E′   T → F T′.
exprstmt : e TK_SEMICOLON ;
e : t eprima ;
eprima : TK_PLUS t eprima | TK_MINUS t eprima | ;
t : f tprima ;
tprima : TK_MULT f tprima | TK_DIV f tprima | ;
f : TK_PLUS f
  | TK_MINUS f
  | NUM
  | STRING
  | ref
  | TK_LPAREN e TK_RPAREN
  | v
  | m
  | h TK_LPAREN e k TK_RPAREN
  ;

// LITERALES Y LLAMADAS
h : ID | TK_TRANSPOSE | TK_DET | TK_TRACE ;
k : TK_COMMA e k | ;
v : TK_LBRACKET n nprima TK_RBRACKET ;
nprima : TK_COMMA n nprima | ;
n : z NUM ;
z : TK_PLUS | TK_MINUS | ;
m : TK_LBRACKET v mprima TK_RBRACKET ;
mprima : TK_COMMA v mprima | ;

// SELECTIVAS
// I → if ( C ) B O   O → else B | ε
i : TK_IF TK_LPAREN c TK_RPAREN b o ;
o : TK_ELSE b | ;
b : TK_LBRACE l TK_RBRACE ;
c : e q ;
q : r e | ;
r : TK_EQ | TK_NEQ | TK_LT | TK_GT ;

// ITERATIVAS
// W → while ( C ) B | for ( As ; C ; As ) B
w : TK_WHILE TK_LPAREN c TK_RPAREN b
  | TK_FOR TK_LPAREN asig TK_SEMICOLON c TK_SEMICOLON asig TK_RPAREN b
  ;
