grammar HedgehogProtocol;

model: message* EOF;

message:
  qualifiedName discriminator=identifier EQUALS label=number LBRACE
    docstring?

    (field | oneof)*
    messageClass*
  RBRACE;

field:
  nested='nested'? rep='repeated'? fieldType=identifier name=identifier EQUALS label=number SEMI;

oneof:
  'oneof' name=identifier LBRACE
    field*
  RBRACE;

messageClass:
  direction qualifiedName LPAREN paramList RPAREN
    docstring? SEMI;

paramList:
  mandatoryParam (COMMA mandatoryParam)* (COMMA repeatedParam)? (COMMA LBRACKET optionalParam (COMMA optionalParam)* RBRACKET)? |
  repeatedParam (COMMA LBRACKET optionalParam (COMMA optionalParam)* RBRACKET)? |
  LBRACKET optionalParam (COMMA optionalParam)* RBRACKET |
  ;

mandatoryParam: identifier;
repeatedParam: STAR identifier;
optionalParam: identifier (SLASH identifier)*;

qualifiedName:
  (path=qualifiedIdentifier DOT)? fileName=identifier DOT name=identifier;

qualifiedIdentifier: identifier (DOT identifier)*;
identifier: IDENTIFIER;
number: NUMBER;
docstring: DOCSTRING;
string: STRING;
direction: (REQ | REP | UPD);

DOCSTRING: '"""' (~'\\' | '\\' .)*? '"""';
STRING: '"' (~'\\' | '\\' .)*? '"';
DOT: '.';
COMMA: ',';
COLON: ':';
SEMI: ';';
SLASH: '/';
EQUALS: '=';
STAR: '*';
REQ: '=>';
REP: '<=';
UPD: '<-';
LPAREN: '(';
RPAREN: ')';
LBRACKET: '[';
RBRACKET: ']';
LBRACE: '{';
RBRACE: '}';
IDENTIFIER: [_a-zA-Z][_a-zA-Z0-9]*;
NUMBER: [0-9]+;

COMMENT: '//' ~[\r\n\f]* -> channel(HIDDEN);
WS: [ \t\r\n\f]+ -> channel(HIDDEN);
