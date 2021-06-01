from lexer import tokens
import ply.yacc as yacc

class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts

    def tree (self):
        return  self.parts


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
    ('left', 'OR'),
    ('left', 'AND')
)

def p_program(p):
    '''program : PROGRAM ID SEMICOLON vars block_function block DOT'''
    p[0] = Node('program', [p[4], p[5], p[6]])

def p_block_function(p):
    ''' block_function : empty
             | block_function function SEMICOLON
            | function SEMICOLON
            |  block_function procedure SEMICOLON
            | procedure SEMICOLON'''
    if len(p) == 4:
        p[0] = p[1].add_parts([p[2]])
    elif len(p)== 3:
        p[0] = Node('funct/proc', [p[1]])
    else:
        p[0] = Node('funct/proc', [p[1]])

def p_block(p):
    '''block : BEGIN statement END'''
    p[0] = Node('block', [p[2]])

def p_vars(p):
    '''vars : empty
            | VAR declarations '''
    if len(p) == 2:
        p[0] = Node('Var', [p[1]])
    else:
        p[0] = Node('Var', [p[2]])

def p_declarations(p):
    '''declarations : id_name COLON typ SEMICOLON
                    | declarations id_name COLON typ SEMICOLON'''
    if len(p) == 5:
        p[0] = Node('declarations', [p[1], p[3]])
    else:
        p[0] = p[1].add_parts([p[2], p[4]])

def p_typ(p):
    '''typ : INTEGER
            | REAL'''
    p[0] = Node('typ', [p[1]])

def p_id_name(p):
    '''id_name : ID
                | id_name COMMA ID'''
    if len(p) == 2:
        p[0] = Node('ID', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_param(p):
    '''param : LPAREN id_name COLON typ RPAREN
            | LPAREN id_name COLON typ SEMICOLON id_name COLON typ RPAREN'''
    if len(p) == 6:
        p[0] = Node('param', [p[2], p[4]])
    else:
        p[0] = Node('param', [p[2], p[4], p[6], p[8]])

def p_procedure(p):
    '''procedure : PROCEDURE ID param SEMICOLON vars block'''
    p[0] = Node('procedure', [p[2], p[3], p[5], p[6]])

def p_function(p):
    '''function : FUNCTION ID param COLON typ SEMICOLON vars block'''
    p[0] = Node('function', [p[2], p[3], p[5], p[7], p[8]])

def p_visf(p):
    '''visf : ID LPAREN id_name RPAREN'''
    p[0] = Node('visf', [p[1], p[3]])

def p_statement(p):
    '''statement : statement vir SEMICOLON
                | vir SEMICOLON '''
    if len(p) == 3:
        p[0] = Node('vir', [p[1]])
    else:
        p[0] = p[1].add_parts([p[2]])

def p_assignstmt(p):
    '''assignstmt : ID PRISV expression
                    | ID PRISV visf'''
    p[0] = Node('assignstmt', [p[1], p[3]])

def p_vir(p):
    '''vir :  assignstmt
            | writestmt
            | ifstmt
            | whilestmt '''
    p[0] = Node('vir', [p[1]])

def p_writestmt(p):
    '''writestmt : WRITE ide'''
    p[0] = Node('writestmt', [p[2]])

def p_ide(p):
    '''ide : LPAREN vn RPAREN'''
    p[0] = Node('ide', [p[2]])

def p_vn(p):
    '''vn : text
            | factor'''
    p[0] = Node('vn', [p[1]])

def p_text(p):
    '''text : STRLIT
            | STRLIT COMMA STRLIT'''
    p[0] = Node('vn', [p[1]])
    if len(p) == 2:
        p[0] = Node('text', [p[1]])
    else:
        p[0] = Node('text', [p[1]])

def p_not(p):
    '''not : NOT
                | empty'''
    p[0] = Node('not', [p[1]])

def p_ifstmt(p):
    '''ifstmt : IF condition THEN vir1
            | IF condition THEN block1'''
    p[0] = Node('ifstmt', [p[2], p[4]])

def p_block1(p):
    '''block1 : BEGIN statement1 END'''
    p[0] = Node('block1', [p[2]])

def p_statement1(p):
    '''statement1 : statement1 vir1 SEMICOLON
                | vir1 SEMICOLON '''
    if len(p) == 3:
        p[0] = Node('statement1', [p[1]])
    else:
        p[0] = p[1].add_parts([p[2]])

def p_vir1(p):
    '''vir1 :  assignstmt
            | writestmt
            | ifstmt
            | whilestmt
            | BREAK
            | CONTINUE'''
    p[0] = Node('vir1', [p[1]])

def p_whilestmt(p):
    '''whilestmt : WHILE condition DO vir
                | WHILE condition DO block'''
    p[0] = Node('whilestmt', [p[2], p[4]])



def p_condition(p):
    '''condition : condition OR condition
                | condition AND condition
                | not LPAREN condition RPAREN
                | not bo'''
    if len(p) == 3:
        p[0] = Node('condition', [p[1], p[2]])
    elif len(p) == 5:
        p[0] = Node('condition', [p[1], p[3]])
    else:
        p[0] = Node('condition', [p[1], p[2], p[3]])

def p_bo(p):
    '''bo : LPAREN expression vibor expression RPAREN'''
    p[0] = Node('bo', [p[2], p[3], p[4]])

def p_vibor(p):
    '''vibor : EQUALLY
            | MIN
            | MINEQ
            | MAX
            | MAXEQ
            | MINMAX'''
    if len(p) == 3:
        p[0] = Node('vibor', [p[1], p[2]])
    else:
        p[0] = Node('vibor', [p[1]])

def p_expression(p):
    '''expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | MINUS expression %prec UMINUS
                   | LPAREN expression RPAREN
                   | integer
                   | real
                   | ID'''
    if len(p) == 2:
        p[0] = Node('factor', [p[1]])
    elif len(p) == 4:
        if p[1]=='(':
            p[0] = Node('expr', [p[2]])
        else:
            p[0] = Node('expr', [p[1], p[2], p[3]])
    else:
        p[0] = Node('umin', [p[1], p[2]])

def p_factor(p):
     '''factor :  integer
                 | real
                 | ID'''
     if len(p) == 2:
         p[0] = Node('factor', [p[1]])


def p_empty(p):
    '''empty : '''
    pass

def p_error(p):
    print('Unexpected token:', p)

def build_tree(code):
    parser = yacc.yacc()
    return parser.parse(code)


# f = open('lex.txt')
# build_tree(f.read())

