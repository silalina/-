import ply.lex as lex

reserved = {
    'program' : 'PROGRAM',
    'var' : 'VAR',
    'begin' : 'BEGIN',
    'integer' : 'INTEGER',
    'real' : 'REAL',
    'if' : 'IF',
    'then' : 'THEN',
    'while' : 'WHILE',
    'do' : 'DO',
    'procedure' : 'PROCEDURE',
    'function' : 'FUNCTION',
    'write' : 'WRITE',
    'not' : 'NOT',
    'and' : 'AND',
    'or' : 'OR',
    'break' : 'BREAK',
    'continue' : 'CONTINUE',
    'end' : 'END'
}

tokens = [
    'integer',
    'real',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'MINEQ',
    'MAXEQ',
    'MAX',
    'MIN',
    'COLON',
    'SEMICOLON',
    'EQUALLY',
    'COMMA',
    'DOT',
    'ID',
    'STRLIT',
    'PRISV',
    'MINMAX'
] + list(reserved.values())

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_PRISV   = r':='
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_MINEQ = r'<='
t_MAXEQ = r'>='
t_MAX  = r'\>'
t_MIN  = r'\<'
t_COLON  = r'\:'
t_SEMICOLON  = r'\;'
t_EQUALLY  = r'\=='
t_COMMA  = r'\,'
t_DOT  = r'\.'
t_MINMAX  = r'\<>'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_real(t):
    r'(\d)+(\.\d+)'
    t.value = float(t.value)
    return t

def t_integer(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_STRLIT(t):
    r'\'{1,1}.{0,}\'{1,1}'
    t.value = str(t.value)
    return t

def t_COMMENT(t):
    r'(\{(.|\n)*\})|(//.*)'
    pass

t_ignore  = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

# f = open('lex.txt')
# data = f.read()
#
# lexer.input(data)
#
# while True:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)
