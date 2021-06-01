import Parser
from Tablsimv import glob_var
from Tablsimv import fp_var

binary_ops = {
    '+': 'add_',
    '-': 'sub_',
    '*': 'mul_',
    '/': 'div_',
    '<': 'lt_',
    '<=': 'le_',
    '>': 'gt_',
    '>=': 'ge_',
    '==': 'eq_',
    '<>': 'ne_',
    '&&': 'and_',
    '||': 'or_'
}

unary_ops = {
    '+': 'uadd',
    '-': 'usub',
    '!': 'not'
}

g = 'global_'
l = 'literal_'
s = 'store_'
r = 'return_'
lo = 'load_'
al = 'alloc_'
p = 'parm_'
pr = 'print_'
u = 'usub_'
n = 'not_'

mas = []
funct =[]
reg = {}

def start():
    f = open('lex.txt')
    parser = Parser.build_tree(f.read())
    vetv = parser.tree()
    return vetv

a=start()

def gen_vrem(type, elem, num):
    vremenno = []
    vremenno.append(type)
    vremenno.append(elem)
    vremenno.append(num)
    return vremenno

def gen_vrem2(type, elem):
    vremenno = []
    vremenno.append(type)
    vremenno.append(elem)
    return vremenno

def gen_vremch(pr, type, num):
    vremenno = []
    vremenno.append(pr)
    if type == 'float':
        vremenno.append(0.0)
    else:
        vremenno.append(0)
    vremenno.append(num)
    return vremenno

def gen_vrem4(type, elem, elem1, num):
    vremenno = []
    vremenno.append(type)
    vremenno.append(elem)
    vremenno.append(elem1)
    vremenno.append(num)
    return vremenno

def opr_type(perem, partfrom):
    if isinstance(perem, int):
        type = 'integer'
    elif isinstance(perem, float):
        type = 'float'
    elif perem[1:4] == 'flo':
        type = 'float'
    elif perem[1:4] == 'int':
        type = 'integer'
    elif isinstance(perem, str):
        tabl_simv = {}
        glob_var(tabl_simv)
        fp_var(tabl_simv)
        if perem == 'global':
            type = tabl_simv[partfrom][perem]
        else:
            type = tabl_simv[partfrom][perem]
        if type == 'real':
            type = 'float'
    return type

def ret_reg(type):
    if (reg.get(type) != None):
        numb = reg.get(type) + 1
        name = "_%s%d" % (type, numb)
        reg[type] = numb
        return name
    else:
        numb = 0
        name = "_%s%d" % (type, numb)
        reg[type] = numb
        return name

def prived_type(elem1, elem2):
    if elem1[1] == 'i' and elem2[1] == 'i':
        type = 'integer'
        return type
    elif elem1[1] == 'f' and elem2[1] == 'f':
        type = 'float'
        return type
    elif elem1[1] == 'f' and elem2[1] == 'i':
        mas = gen_vrem('prived_float', elem2, ret_reg('float'))
        return mas
    elif elem1[1] == 'i' and elem2[1] == 'f':
        mas = gen_vrem('prived_float', elem1, ret_reg('float'))
        return mas

def vars_glob():
    mas.append(('func', '_init', 'void'))
    if (a[0] != None):
        for i in range(0, len(a[0].parts[0].parts)):
            for j in range(0, len(a[0].parts[0].parts[i].parts)):
                if a[0].parts[0].parts[i].parts[j]!='real' and a[0].parts[0].parts[i].parts[j]!='integer':
                    if a[0].parts[0].parts[i+1].parts[0] == 'real':
                        type = 'float'
                    else:
                        type = a[0].parts[0].parts[i+1].parts[0]
                    mas.append(tuple(gen_vrem2(g+type, a[0].parts[0].parts[i].parts[j])))
                    num = ret_reg(type)
                    mas.append(tuple(gen_vremch(l+type, type, num)))
                    mas.append(tuple(gen_vrem(s+type, num, a[0].parts[0].parts[i].parts[j])))
    mas.append(('return_void',))
    return mas

def param(elem):      #в каждой функции/процедуре с нуля индекс
    num = 0
    mas = []
    if (elem != None):
        for i in range(0, len(elem.parts)):
            for j in range(0, len(elem.parts[i].parts)):
                if elem.parts[i].parts[j]!='real' and elem.parts[i].parts[j]!='integer':
                    if elem.parts[i+1].parts[0] == 'real':
                        type = 'float'
                    else:
                        type = elem.parts[i+1].parts[0]
                    mas.append(tuple(gen_vrem(p+type, elem.parts[i].parts[j], num)))
                    num +=1
    return mas

def vars_loc(elem):
    mas = []
    if (elem != None):
        for i in range(0, len(elem.parts[0].parts)):
            for j in range(0, len(elem.parts[0].parts[i].parts)):
                if elem.parts[0].parts[i].parts[j]!='real' and elem.parts[0].parts[i].parts[j]!='integer':
                    if elem.parts[0].parts[i+1].parts[0] == 'real':
                        type = 'float'
                    else:
                        type = elem.parts[0].parts[i+1].parts[0]
                    mas.append(tuple(gen_vrem2(al+type, elem.parts[0].parts[i].parts[j])))
                    num = ret_reg(type)
                    mas.append(tuple(gen_vremch(l+type, type, num)))
                    mas.append(tuple(gen_vrem(s+type, num, elem.parts[0].parts[i].parts[j])))
    return mas
    # for i in range(len(mas)):
    #     print(mas[i])
    #     print()

def operation(elem):
    zn = binary_ops[elem]
    return zn

def statement(elem, partfrom):
    mas = []
    if elem.type == 'block':
        mas = statement(elem.parts[0], partfrom)
        return mas
    if elem.parts[0].type == 'vir':
        for i in range(len(elem.parts)):
            if elem.parts[i].parts[0].type == 'writestmt':
               mas1 = write(elem.parts[i].parts[0], partfrom)
               for i in range(len(mas1)):
                   mas.append(mas1[i])
            elif elem.parts[i].parts[0].type == 'assignstmt':
                mas1 = assignstmt(elem.parts[i].parts[0], partfrom)
                for i in range(len(mas1)):
                    mas.append(mas1[i])
            elif elem.parts[i].parts[0].type == 'ifstmt':
                mas.append(('block_if',))
                mas1 = ifstmt(elem.parts[i].parts[0], partfrom)
                mas.append(mas1)
            elif elem.parts[i].parts[0].type == 'whilestmt':
                mas.append(('block_while',))
                mas1 = whilestmt(elem.parts[i].parts[0], partfrom)
                mas.append(mas1)
        return mas
    else:
        if elem.parts[0].type == 'writestmt':
            mas1 = write(elem.parts[0], partfrom)
            for i in range(len(mas1)):
                mas.append(mas1[i])
        elif elem.parts[0].type == 'assignstmt':
            mas1 = assignstmt(elem.parts[0], partfrom)
            for i in range(len(mas1)):
                mas.append(mas1[i])
        elif elem.parts[0].type == 'ifstmt':
            mas.append(('block_if',))
            mas1 = ifstmt(elem.parts[0], partfrom)
            mas.append(mas1)
        elif elem.parts[0].type == 'whilestmt':
            mas.append(('block_while',))
            mas1 = whilestmt(elem.parts[0], partfrom)
            mas.append(mas1)
        return mas

def statement1(elem, partfrom):
    mas = []
    if elem.type == 'block1':
        mas = statement1(elem.parts[0], partfrom)
        return mas
    if elem.parts[0].type == 'vir1':
        for i in range(len(elem.parts)):
            if elem.parts[i].parts[0] == 'break':
                mas.append(('break',))
            elif elem.parts[i].parts[0] == 'continue':
                mas.append(('continue',))
            elif elem.parts[i].parts[0].type == 'writestmt':
                mas1 = write(elem.parts[i].parts[0], partfrom)
                for i in range(len(mas1)):
                    mas.append(mas1[i])
            elif elem.parts[i].parts[0].type == 'assignstmt':
                mas1 = assignstmt(elem.parts[i].parts[0], partfrom)
                for i in range(len(mas1)):
                    mas.append(mas1[i])
            elif elem.parts[i].parts[0].type == 'ifstmt':
                mas.append(('block_if',))
                mas1 = ifstmt(elem.parts[i].parts[0], partfrom)
                mas.append(mas1)
            elif elem.parts[i].parts[0].type == 'whilestmt':
                mas.append(('block_while',))
                mas1 = whilestmt(elem.parts[i].parts[0], partfrom)
                mas.append(mas1)
        return mas
    else:
        if elem.parts[0].type == 'writestmt':
            mas1 = write(elem.parts[0], partfrom)
            for i in range(len(mas1)):
                mas.append(mas1[i])
        elif elem.parts[0].type == 'assignstmt':
            mas1 = assignstmt(elem.parts[0], partfrom)
            for i in range(len(mas1)):
                mas.append(mas1[i])
        elif elem.parts[0].type == 'ifstmt':
            mas.append(('block_if',))
            mas1 = ifstmt(elem.parts[0], partfrom)
            mas.append(mas1)
        elif elem.parts[0].type == 'whilestmt':
            mas.append(('block_while',))
            mas1 = whilestmt(elem.parts[0], partfrom)
            mas.append(mas1)
        return mas

def posl_elem(elem):
    q = elem[len(elem)-1][len(elem[len(elem)-1])-1]
    return q

def predposl_elem(elem):
    q = elem[len(elem)-1][len(elem[len(elem)-1])-2]
    return q

def umin(elem, partfrom):
    mas = []
    if len(elem.parts) == 3:
        mas1 = []
        mas2 = []
        if elem.parts[0].type == 'umin':
            mas = umin(elem.parts[0], partfrom)
        elif elem.parts[0].type == 'expr':
            mas = expression(elem.parts[0], partfrom)
        elif elem.parts[0].type == 'factor':
            type = opr_type(elem.parts[0], partfrom)
            mas = gen_vrem(type, elem.parts[0], ret_reg(type))
        if elem.parts[2].type == 'umin':
            mas2 = umin(elem.parts[2], partfrom)
        elif elem.parts[2].type == 'expr':
            mas2 = expression(elem.parts[2], partfrom)
        elif elem.parts[2].type == 'factor':
            type = opr_type(elem.parts[2].parts[0], partfrom)
            mas.append(tuple(gen_vrem(type, elem.parts[2].parts[0], ret_reg(type))))
        p = prived_type(posl_elem(mas), posl_elem(mas2))
        if p != 'integer' and p != 'float':
            mas.append(p)
            type = opr_type(posl_elem(mas))
        else:
            type = p
        q = gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), posl_elem(mas2), ret_reg(type))
        for i in range(len(mas2)):
            mas.append(mas2[i])
        mas.append(tuple(q))
        return mas
    elif len(elem.parts) == 2:
        if elem.parts[1].type == 'umin':
            mas = umin(elem.parts[1], partfrom)
            type = opr_type(elem.parts[1].parts[0], partfrom)
            mas.append(tuple(gen_vrem(u+type, elem.parts[1].parts[0], ret_reg(type))))
            return mas
        elif elem.parts[1].type == 'expr':
            mas = expression(elem.parts[1], partfrom)
            type = opr_type(elem.parts[1].parts[0], partfrom)
            mas.append(tuple(gen_vrem(u+type, elem.parts[1].parts[0], ret_reg(type))))
            return mas
        elif elem.parts[1].type == 'factor':
            type = opr_type(elem.parts[1].parts[0], partfrom)
            if isinstance(elem.parts[1].parts[0], (float, int)):
                mas.append(tuple(gen_vrem(l+type, elem.parts[1].parts[0], ret_reg(type))))
            else:
                mas.append(tuple(gen_vrem(lo+type, elem.parts[1].parts[0], ret_reg(type))))
            mas.append(tuple(gen_vrem(u+type, posl_elem(mas), ret_reg(type))))
            return mas

def write(elem, partfrom):
    mas = []
    vremenno = []
    if elem.parts[0].parts[0].parts[0].type == 'factor':
        type = opr_type(elem.parts[0].parts[0].parts[0].parts[0], partfrom)
        num = ret_reg(type)
        mas.append(tuple(gen_vrem(lo+type, elem.parts[0].parts[0].parts[0].parts[0], num)))
        mas.append(tuple(gen_vrem2(pr+type, num)))
        return mas
    elif elem.parts[0].parts[0].parts[0].type == 'text':
        type = 'str'
        num = ret_reg(type)
        mas.append(tuple(gen_vrem(l+type, elem.parts[0].parts[0].parts[0].parts[0], num)))
        mas.append(tuple(gen_vrem2(pr+type, num)))
        return mas
    else:
        type = opr_type(elem.parts[0].parts[0].parts[0].parts[0], partfrom)
        num = ret_reg(type)
        mas.append(tuple(gen_vrem(lo+type, elem.parts[0].parts[0].parts[0].parts[0].parts[0], num)))
        mas.append(tuple(gen_vrem2(pr+type, num)))
        return mas

def assignstmt(elem, partfrom):
    mas = []
    if elem.parts[1].type == 'visf':
        num = opr_type(elem.parts[1].parts[0], elem.parts[1].parts[0])
        for i in range(len(elem.parts[1].parts[1].parts)):
            type = opr_type(elem.parts[1].parts[1].parts[i], partfrom)
            nump = ret_reg(type)
            mas.append(tuple(gen_vrem(lo+type, elem.parts[1].parts[1].parts[i], nump)))
        q = ret_reg(num)
        mas.append(tuple(gen_vrem4('call_func', elem.parts[1].parts[0], nump, q)))
        mas.append(tuple(gen_vrem(s+num, q, elem.parts[0])))
    else:
        type = opr_type(elem.parts[0], partfrom)
        mas1 = expression(elem.parts[1], partfrom, l)
        for i in range(len(mas1)):
            mas.append(mas1[i])
        mas.append(tuple(gen_vrem(s+type, posl_elem(mas1), elem.parts[0])))
    return mas

def expression(elem, partfrom, l):
    mas = []
    if elem.type == 'factor':
        type = opr_type(elem.parts[0], partfrom)
        if isinstance(elem.parts[0], (int, float)):
            mas.append(tuple(gen_vrem('literal_'+type, elem.parts[0], ret_reg(type))))
        else:
            mas.append(tuple(gen_vrem(lo+type, elem.parts[0], ret_reg(type))))
        return mas
    elif elem.type == 'umin':
        mas = umin(elem, partfrom)
        return mas
    else:
        if len(elem.parts) == 3:
            if elem.parts[0].type == 'expr':
                mas1 = expression(elem.parts[0], partfrom, l)
                if elem.parts[2].type == 'expr':    # exp-exp
                    mas2 = expression(elem.parts[2], partfrom, l)
                    for i in range(len(mas1)):
                        mas.append(mas1[i])
                    for i in range(len(mas2)):
                        mas.append(mas2[i])
                    p = prived_type(posl_elem(mas1), posl_elem(mas2))
                    if p != 'integer' and p != 'float':
                        mas.append(tuple(p))
                        type = opr_type(posl_elem(mas), partfrom)
                        if posl_elem(mas1)[1:4] == 'flo':
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas), ret_reg(type))))
                        else:
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), posl_elem(mas2), ret_reg(type))))
                    else:
                        type = p
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas2), ret_reg(type))))
                    return mas
                elif elem.parts[2].type == 'factor':  #exp-factor
                    type = opr_type(elem.parts[2].parts[0], partfrom)
                    num = ret_reg(type)
                    type = opr_type(elem.parts[2].parts[0], partfrom)
                    if isinstance(elem.parts[2].parts[0], (int, float)):
                        mas.append(tuple(gen_vrem('literal_'+type, elem.parts[2].parts[0], num)))
                    else:
                        mas.append(tuple(gen_vrem(lo+type, elem.parts[2].parts[0], num)))
                    for i in range(len(mas1)):
                        mas.append(mas1[i])
                    p = prived_type(posl_elem(mas1), num)
                    if p != 'integer' and p != 'float':
                        mas.append(tuple(p))
                        type = opr_type(posl_elem(mas), partfrom)
                        if posl_elem(mas1)[1:4] == 'flo':
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas), ret_reg(type))))
                        else:
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), num, ret_reg(type))))
                    else:
                        type = p
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), num, ret_reg(type))))
                    return mas
                elif elem.parts[2].type == 'umin':
                    mas2 = umin(elem.parts[2], partfrom)
                    for i in range(len(mas1)):
                        mas.append(mas1[i])
                    for i in range(len(mas2)):
                        mas.append(mas2[i])
                    p = prived_type(posl_elem(mas1), posl_elem(mas2))
                    if p != 'integer' and p != 'float':
                        mas.append(tuple(p))
                        type = opr_type(posl_elem(mas), partfrom)
                        if posl_elem(mas1)[1:4] == 'flo':
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas), ret_reg(type))))
                        else:
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), posl_elem(mas2), ret_reg(type))))
                    else:
                        type = p
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas2), ret_reg(type))))
                    return mas
            elif elem.parts[0].type == 'factor' and elem.parts[2].type == 'expr': #fact-expr
                mas = expression(elem.parts[2], partfrom, l)
                q = posl_elem(mas)
                type = opr_type(elem.parts[0].parts[0], partfrom)
                num = ret_reg(type)
                if isinstance(elem.parts[0].parts[0], (int, float)):
                    mas.append(tuple(gen_vrem('literal_'+type, elem.parts[0].parts[0], num)))
                else:
                    mas.append(tuple(gen_vrem(lo+type, elem.parts[0].parts[0], num)))
                p = prived_type(num, q)
                if p != 'integer' and p != 'float':
                    mas.append(tuple(p))
                    type = opr_type(posl_elem(mas), partfrom)
                    if num[1:4] == 'flo':
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num, posl_elem(mas), ret_reg(type))))
                    else:
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), q, ret_reg(type))))
                else:
                    type = p
                    mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num, q, ret_reg(type))))
                return mas
            else:
                if elem.parts[0].type == 'umin':
                    mas1 = umin(elem.parts[0], partfrom)
                    if elem.parts[2].type == 'umin':  #umin-umin
                        mas2 = umin(elem.parts[2], partfrom)
                        for i in range(len(mas1)):
                            mas.append(mas1[i])
                        for i in range(len(mas2)):
                            mas.append(mas2[i])
                        p = prived_type(posl_elem(mas1), posl_elem(mas2))
                        if p != 'integer' and p != 'float':
                            mas.append(tuple(p))
                            type = opr_type(posl_elem(mas), partfrom)
                            if posl_elem(mas1)[1:4] == 'flo':
                                mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas), ret_reg(type))))
                            else:
                                mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), posl_elem(mas2), ret_reg(type))))
                        else:
                            type = p
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas2), ret_reg(type))))
                        return mas
                    elif elem.parts[2].type == 'factor':  #umin-factor
                        type = opr_type(elem.parts[2].parts[0], partfrom)
                        num = ret_reg(type)
                        if isinstance(elem.parts[2].parts[0], (int, float)):
                            mas.append(tuple(gen_vrem('literal_'+type, elem.parts[2].parts[0], num)))
                        else:
                            mas.append(tuple(gen_vrem(lo+type, elem.parts[2].parts[0], num)))
                        for i in range(len(mas1)):
                            mas.append(mas1[i])
                        p = prived_type(posl_elem(mas1), num)
                        if p != 'integer' and p != 'float':
                            mas.append(tuple(p))
                            type = opr_type(posl_elem(mas), partfrom)
                            if posl_elem(mas1)[1:4] == 'flo':
                                mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), posl_elem(mas), ret_reg(type))))
                            else:
                                mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), num, ret_reg(type))))
                        else:
                            type = p
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas1), num, ret_reg(type))))
                        return mas
                elif elem.parts[2].type == 'umin' and elem.parts[0].type == 'factor':      #factor-umin
                    mas1 = umin(elem.parts[0], partfrom)
                    type = opr_type(elem.parts[0].parts[0], partfrom)
                    num = ret_reg(type)
                    if isinstance(elem.parts[0].parts[0], (int, float)):
                        mas.append(tuple(gen_vrem('literal_'+type, elem.parts[0].parts[0], num)))
                    else:
                        mas.append(tuple(gen_vrem(lo+type, elem.parts[0].parts[0], num)))
                    for i in range(len(mas1)):
                        mas.append(mas1[i])
                    p = prived_type(num, posl_elem(mas1))
                    if p != 'integer' and p != 'float':
                        mas.append(tuple(p))
                        type = opr_type(posl_elem(mas), partfrom)
                        if num[1:4] == 'flo':
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num, posl_elem(mas), ret_reg(type))))
                        else:
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), posl_elem(mas1), ret_reg(type))))
                    else:
                        type = p
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num, posl_elem(mas1), ret_reg(type))))
                    return mas
                elif elem.parts[0].type == 'factor' and elem.parts[2].type == 'factor':
                    type1 = opr_type(elem.parts[0].parts[0], partfrom)
                    num1 = ret_reg(type1)
                    type2 = opr_type(elem.parts[2].parts[0], partfrom)
                    num2 = ret_reg(type2)
                    if isinstance(elem.parts[0].parts[0], (int, float)):
                        mas.append(tuple(gen_vrem('literal_'+type1, elem.parts[0].parts[0], num1)))
                    else:
                        mas.append(tuple(gen_vrem(lo+type1, elem.parts[0].parts[0], num1)))
                    if isinstance(elem.parts[2].parts[0], (int, float)):
                        mas.append(tuple(gen_vrem('literal_'+type2, elem.parts[2].parts[0], num2)))
                    else:
                        mas.append(tuple(gen_vrem(lo+type2, elem.parts[2].parts[0], num2)))
                    p = prived_type(num1, num2)
                    if p != 'integer' and p != 'float':
                        mas.append(tuple(p))
                        type = opr_type(posl_elem(mas), partfrom)
                        if num1[1:4] == 'flo':
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num1, posl_elem(mas), ret_reg(type))))
                        else:
                            mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, posl_elem(mas), num2, ret_reg(type))))
                    else:
                        type = p
                        mas.append(tuple(gen_vrem4(operation(elem.parts[1])+type, num1, num2, ret_reg(type))))
                    return mas
        elif elem.parts[0].type == 'expr':
            mas = expression(elem.parts[0], partfrom, l)
            return mas
        elif elem.parts[0].type == 'umin':
            mas = umin(elem.parts[1], partfrom)
            type = opr_type(elem.parts[1].parts[0], partfrom)
            mas.append(tuple(gen_vrem(u+type, elem.parts[1].parts[0], ret_reg(type))))
            return mas
        elif elem.parts[0].type == 'factor':
            print('-----------------------------')
            print(elem.part[0])
            print('-----------------------------')
            type = opr_type(elem.parts[1].parts[0], partfrom)
            if isinstance(elem.parts[1].parts[0], (int, float)):
                mas.append(tuple(gen_vrem('literal_'+type, elem.parts[1].parts[0], ret_reg(type))))
            else:
                mas.append(tuple(gen_vrem(lo+type, elem.parts[1].parts[0], ret_reg(type))))
            return mas

def bo(elem, partfrom):                                        #переделать приведение типов
    mas = expression(elem.parts[0], partfrom, lo)
    q = posl_elem(mas)
    mas2 = expression(elem.parts[2], partfrom, lo)
    for i in range(len(mas2)):
        mas.append(tuple(mas2[i]))
    vib = binary_ops[elem.parts[1].parts[0]]
    p = prived_type(q, posl_elem(mas2))
    if p != 'integer' and p != 'float':
        mas.append(tuple(p))
        if q[1:4] == 'flo':
            mas.append(tuple(gen_vrem4(vib+'float', q, posl_elem(mas), ret_reg('bool'))))
        else:
            mas.append(tuple(gen_vrem4(vib+'integer', posl_elem(mas), posl_elem(mas2), ret_reg('bool'))))
    else:
        mas.append(tuple(gen_vrem4(vib+p, q, posl_elem(mas2), ret_reg('bool'))))
    return mas

def condition(elem, partfrom):                     #здесь нужно доделать несколько скобок
    if len(elem.parts) == 2:
        mas = bo(elem.parts[1], partfrom)
        if elem.parts[0].parts[0] is not None:
            mas.append(tuple(gen_vrem(n+'bool', posl_elem(mas), ret_reg('bool'))))
        return mas
    elif len(elem.parts) == 3:
        mas = condition(elem.parts[0], partfrom)
        mas1 = condition(elem.parts[2], partfrom)
        p = posl_elem(mas)
        for i in range(len(mas1)):
            mas.append(mas1[i])
        mas.append(tuple(gen_vrem4(elem.parts[1]+'_bool', p, posl_elem(mas1), ret_reg('bool'))))
        return mas

def ifstmt(elem, partfrom):
    mas = []
    mas.append(condition(elem.parts[0], partfrom))
    mas1 = statement1(elem.parts[1], partfrom)
    mas.append(mas1)
    return mas

# def ifstmt(elem, partfrom):
#     mas = []
#     mas.append(condition(elem.parts[0], partfrom))
#     if elem.parts[1].type == 'block1':
#         mas1 = statement(elem.parts[1].parts[0].parts[0], partfrom)
#         mas.append(mas1)
#     else:
#         mas1 = statement(elem.parts[1], partfrom)
#         mas.append(mas1)
#     return mas

def whilestmt(elem, partfrom):
    mas = []
    mas.append(condition(elem.parts[0], partfrom))
    mas1 = statement(elem.parts[1], partfrom)
    mas.append(mas1)
    return mas

# def whilestmt(elem, partfrom):
#     mas = []
#     mas.append(condition(elem.parts[0], partfrom))
#     if elem.parts[1].type == 'block':
#         if elem.parts[1].parts[0].type == 'vir' and elem.parts[1].parts[0].parts[0].type == 'vir':
#             for i in range(len(elem.parts[1].parts[0].parts)):
#                 mas1 = statement(elem.parts[1].parts[0].parts[i], partfrom)
#                 mas.append(mas1)
#             return mas
#         else:
#             mas1 = statement(elem.parts[1].parts[0], partfrom)
#             mas.append(mas1)
#             return mas
#     else:
#         if elem.parts[1].type == 'vir':
#             mas1 = statement(elem.parts[1], partfrom)
#             mas.append(mas1)
#         return mas

# def full_prog():
#     print('-------------------------------ГЛОБАЛ ВАРЫ------------------------------------------')
#     vars_glob()    #   a[0]
#     for i in range(len(a[1].parts)):  #    a[1] - это функции и процедуры
#         partfrom = a[1].parts[i].parts[0]
#         print('----------------------------'+a[1].parts[i].type + ' ' + a[1].parts[i].parts[0]+'---------------------------------')
#         print('-----------------param---------------------------')
#         param(a[1].parts[i].parts[1])
#         print('----------------------------ЛОКАЛ ВАРЫ-----------------------------')
#         if a[1].parts[i].type == 'function':
#             vars_loc(a[1].parts[i].parts[3])
#         else:
#             vars_loc(a[1].parts[i].parts[2])
#
#     g = 'global'
#     # for i in range(len(a[2].parts[0].parts)):                      #     main блок ---> global
#     #     statement(a[2].parts[0].parts[i])
#
# full_prog()       #переменные global/local хранятся в локальных mas

# print('------------------------------------IF-----------------------------------')
# ifi = ifstmt(a[2].parts[0].parts[3].parts[0], 'global')
# for i in range(len(ifi)):
#     print(ifi[i])
#
# print('-----------------------------------WHILE---------------------------------')
# whil = whilestmt(a[2].parts[0].parts[6].parts[0], 'global')
# for i in range(len(whil)):
#     print(whil[i])

# q = statement(a[2], 'global')
# for i in range(len(q)):
#     print(q[i])

mas = [vars_glob()]

def tac(a):
    for k in range(len(a[1].parts)):
        masp = []
        mas1 = []
        masl = []
        masd = []
        masgl = []
        typeel = []
        if a[1].parts[0] == None:
            break
        if (a[1].parts[k].parts[0] != None):
            for i in range(len(a[1].parts[k].parts[1].parts)):
                for j in range(len(a[1].parts[k].parts[1].parts[i].parts)):
                    if a[1].parts[k].parts[1].parts[i].parts[j]!='real' and a[1].parts[k].parts[1].parts[i].parts[j]!='integer':
                        if a[1].parts[k].parts[1].parts[i+1].parts[0] == 'real':
                            typeel.append('float')
                        elif a[1].parts[k].parts[1].parts[i+1].parts[0] == 'integer':
                            typeel.append(a[1].parts[k].parts[1].parts[i+1].parts[0])
        if a[1].parts[k].type == 'function':
            mas1 = gen_vrem2(a[1].parts[k].type, a[1].parts[k].parts[0])
            for f in range(len(typeel)):
                mas1.append(typeel[f])
            if a[1].parts[k].parts[2].parts[0] == 'real':
                mas1.append('float')
            else:
                mas1.append('integer')
        elif a[1].parts[k].type == 'procedure':
            mas1 = gen_vrem2(a[1].parts[k].type, a[1].parts[k].parts[0])
            for f in range(len(typeel)):
                mas1.append(typeel[f])
        masp = [tuple(mas1)]
        q = param(a[1].parts[k].parts[1])
        masp.append(q)
        #локальные вары
        if a[1].parts[k].type == 'function':
            type = a[1].parts[k].parts[2].parts[0]
            if type == 'real':
                type = 'float'
            # print(a[1].parts[k].parts[2].parts[0])//type
            # print(a[1].parts[k].parts[0])//name
            st1 = tuple(gen_vrem2(al+type, a[1].parts[k].parts[0]))
            if type == 'float':
                st2 = tuple(gen_vrem(l+type, 0.0, ret_reg(type)))
            else:
                st2 = tuple(gen_vrem(l+type, 0, ret_reg(type)))
            masl = vars_loc(a[1].parts[k].parts[3])
            masl.insert(0, st1)
            masl.insert(1, st2)
        else:
            masl = vars_loc(a[1].parts[k].parts[2])
        masp.append(masl)
        masd = statement(a[1].parts[k].parts[len(a[1].parts[k].parts)-1], a[1].parts[k].parts[0])
        if a[1].parts[k].type == 'procedure':
            masd.append(('return_void',))
        else:
            if a[1].parts[0].parts[2].parts[0] == 'real':
                type = 'float'
            else:
                type = 'integer'
            num = ret_reg(type)
            masd.append(tuple(gen_vrem(lo+type, a[1].parts[0].parts[0], num)))
            masd.append(tuple(gen_vrem2('return_'+type, num)))
        masp.append(masd)
        mas.append(masp)
    masgl.append(tuple(gen_vrem('func', '_main', 'void')))
    mash = statement(a[2], 'global')
    mash.append(('return_void',))
    masgl.append(mash)
    mas.append(masgl)
    return mas

# q = tac(a)
# for func in q:
#     print(func)
