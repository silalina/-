import tempfile

from llvmlite import binding
from llvmlite.ir import (
    Module, IRBuilder, Function, IntType, DoubleType, VoidType, Constant,
    GlobalVariable, FunctionType, ArrayType
)
con = []
br = []

class Block(object):

    def __init__(self):
        self.instructions = []   # Instructions in the block
        self.next_block = None    # Link to the next block

    def append(self, instr):
        self.instructions.append(instr)

    def __iter__(self):
        return iter(self.instructions)


class BlockVisitor(object):
    '''
    Class for visiting basic blocks.  Define a subclass and define
    methods such as visit_BasicBlock or visit_IfBlock to implement
    custom processing (similar to ASTs).
    '''

    def visit(self, block):
        while isinstance(block, Block):
            name = "visit_%s" % type(block).__name__
            if hasattr(self, name):
                getattr(self, name)(block)
            block = block.next_block


integer_type = IntType(32)
float_type = DoubleType()
bool_type = IntType(1)
void_type = VoidType()

typemap = {
    'integer': integer_type,
    'float': float_type,
    'bool': bool_type,
    'void': void_type
}

reg = {}
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


class GenerateLLVM(object):

    def __init__(self, name='module'):

        self.module = Module(name)
        self.module.triple = binding.get_default_triple()
        self.block = None
        self.builder = None
        self.globals = {}
        self.locals = {}
        self.temps = {}
        self.write()
        self.last_branch = None

    def write(self):
        self.printf= Function(self.module, FunctionType(IntType(32), [IntType(8).as_pointer()], var_arg=True), name="printf")

    def start_function(self, name, rettypename, parmtypenames):
        rettype = typemap[rettypename]
        parmtypes = [typemap[pname] for pname in parmtypenames]
        func_type = FunctionType(rettype, parmtypes)
        self.function = Function(self.module, func_type, name=name)
        self.block = self.function.append_basic_block("entry")
        self.builder = IRBuilder(self.block)
        self.exit_block = self.function.append_basic_block("exit")
        self.locals = {}
        self.temps = {}
        if rettype is not void_type:
            self.locals['return'] = self.builder.alloca(rettype, name="return")

        # Put an entry in the globals
        self.globals[name] = self.function

    def new_basic_block(self, name=''):
        self.builder = IRBuilder(self.block.instructions)
        return self.function.append_basic_block(name)


    def generate_code(self, ircode):
        for opcode, *args in ircode:
            if hasattr(self, 'emit_' + opcode):
                getattr(self, 'emit_' + opcode)(*args)



    def terminate(self):
        # Add a return statement. This connects the last block to the exit
        # block.
        # The return statement is then emitted
        if self.last_branch != self.block:
            self.builder.branch(self.exit_block)
        self.builder.position_at_end(self.exit_block)

        if 'return' in self.locals:
            self.builder.ret(self.builder.load(self.locals['return']))
        else:
            self.builder.ret_void()

    def add_block(self, name):
        # Add a new block to the existing function
        return self.function.append_basic_block(name)

    def set_block(self, block):
        # Sets the current block for adding more code
        self.block = block
        self.builder.position_at_end(block)

    def cbranch(self, testvar, true_block, false_block):
        self.builder.cbranch(self.temps[testvar], true_block, false_block)

    def branch(self, next_block):
        if self.last_branch != self.block:
            self.builder.branch(next_block)
        self.last_branch = self.block
    # ----------------------------------------------------------------------
    # Opcode implementation.   You must implement the opcodes.  A few
    # sample opcodes have been given to get you started.
    # ----------------------------------------------------------------------

    # Creation of literal values.  Simply define as LLVM constants.
    def emit_literal_integer(self, value, target):
        self.temps[target] = Constant(integer_type, value)

    def emit_literal_float(self, value, target):
        self.temps[target] = Constant(float_type, value)

    def emit_literal_bool(self, value, target):
        self.temps[target] = Constant(bool_type, value)

    def emit_literal_str(self, value, target):
        value=value+'\0'
        c_str_val = Constant(ArrayType(IntType(8), len(value)), bytearray(value.encode("utf8")))
        var = self.builder.alloca(c_str_val.type, name=target)
        self.builder.store(c_str_val, var)
        self.temps[target] = var

    def emit_alloc_integer(self, name):
        var = self.builder.alloca(integer_type, name=name)
        var.initializer = Constant(integer_type, 0)
        self.locals[name] = var

    def emit_alloc_float(self, name):
        var = self.builder.alloca(float_type, name=name)
        var.initializer = Constant(float_type, 0)
        self.locals[name] = var

    def emit_alloc_bool(self, name):
        var = self.builder.alloca(bool_type, name=name)
        var.initializer = Constant(bool_type, 0)
        self.locals[name] = var

    def emit_global_integer(self, name):
        var = GlobalVariable(self.module, integer_type, name=name)
        var.initializer = Constant(integer_type, 0)
        self.globals[name] = var

    def emit_global_float(self, name):
        var = GlobalVariable(self.module, float_type, name=name)
        var.initializer = Constant(float_type, 0)
        self.globals[name] = var

    def emit_global_bool(self, name):
        var = GlobalVariable(self.module, bool_type, name=name)
        var.initializer = Constant(bool_type, 0)
        self.globals[name] = var

    def lookup_var(self, name):
        if name in self.locals:
            return self.locals[name]
        else:
            return self.globals[name]

    def emit_load_integer(self, name, target):
        # print('LOADINT %s, %s' % (name, target))
        # print('GLOBALS %s' % self.globals)
        # print('LOCALS %s' % self.locals)
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_load_float(self, name, target):
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_load_bool(self, name, target):
        self.temps[target] = self.builder.load(self.lookup_var(name), target)

    def emit_store_integer(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    def emit_store_float(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    def emit_store_bool(self, source, target):
        self.builder.store(self.temps[source], self.lookup_var(target))

    # Binary + operator
    def emit_add_integer(self, left, right, target):
        self.temps[target] = self.builder.add(
            self.temps[left], self.temps[right], target)

    def emit_add_float(self, left, right, target):
        self.temps[target] = self.builder.fadd(
            self.temps[left], self.temps[right], target)

    # Binary - operator
    def emit_sub_integer(self, left, right, target):
        self.temps[target] = self.builder.sub(
            self.temps[left], self.temps[right], target)

    def emit_sub_float(self, left, right, target):
        self.temps[target] = self.builder.fsub(
            self.temps[left], self.temps[right], target)

    # Binary * operator
    def emit_mul_integer(self, left, right, target):
        self.temps[target] = self.builder.mul(
            self.temps[left], self.temps[right], target)

    def emit_mul_float(self, left, right, target):
        self.temps[target] = self.builder.fmul(
            self.temps[left], self.temps[right], target)

    # Binary / operator
    def emit_div_integer(self, left, right, target):
        self.temps[target] = self.builder.sdiv(
            self.temps[left], self.temps[right], target)

    def emit_div_float(self, left, right, target):
        self.temps[target] = self.builder.fdiv(
            self.temps[left], self.temps[right], target)

    # Unary - operator
    def emit_usub_integer(self, source, target):
        self.temps[target] = self.builder.sub(
            Constant(integer_type, 0),
            self.temps[source],
            target)

    def emit_usub_float(self, source, target):
        self.temps[target] = self.builder.fsub(
            Constant(float_type, 0.0),
            self.temps[source],
            target)

    # Binary < operator
    def emit_lt_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '<', self.temps[left], self.temps[right], target)

    def emit_lt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '<', self.temps[left], self.temps[right], target)

    # Binary <= operator
    def emit_le_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '<=', self.temps[left], self.temps[right], target)

    def emit_le_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '<=', self.temps[left], self.temps[right], target)

    # Binary > operator
    def emit_gt_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '>', self.temps[left], self.temps[right], target)

    def emit_gt_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '>', self.temps[left], self.temps[right], target)

    # Binary >= operator
    def emit_ge_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '>=', self.temps[left], self.temps[right], target)

    def emit_ge_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '>=', self.temps[left], self.temps[right], target)

    # Binary == operator
    def emit_eq_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '==', self.temps[left], self.temps[right], target)

    def emit_eq_bool(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '==', self.temps[left], self.temps[right], target)

    def emit_eq_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '==', self.temps[left], self.temps[right], target)

    # Binary != operator
    def emit_ne_integer(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '!=', self.temps[left], self.temps[right], target)

    def emit_ne_bool(self, left, right, target):
        self.temps[target] = self.builder.icmp_signed(
            '!=', self.temps[left], self.temps[right], target)

    def emit_ne_float(self, left, right, target):
        self.temps[target] = self.builder.fcmp_ordered(
            '!=', self.temps[left], self.temps[right], target)

    # Binary && operator
    def emit_and_bool(self, left, right, target):
        self.temps[target] = self.builder.and_(
            self.temps[left], self.temps[right], target)

    # Binary || operator
    def emit_or_bool(self, left, right, target):
        self.temps[target] = self.builder.or_(
            self.temps[left], self.temps[right], target)

    # Unary ! operator
    def emit_not_bool(self, source, target):
        self.temps[target] = self.builder.icmp_signed(
            '==', self.temps[source], Constant(bool_type, 0), target)
    # Print statements

    def emit_print_integer(self, source):
        value=self.temps[source]
        voidptr_ty = IntType(8).as_pointer()
        fmt = "%i \n\0"
        c_fmt = Constant(ArrayType(IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
        global_fmt = GlobalVariable(self.module, c_fmt.type, name=ret_reg('fstr'))
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(self.printf, [fmt_arg, value])

    def emit_print_float(self, source):
        value=self.temps[source]
        voidptr_ty = IntType(8).as_pointer()
        fmt = "%f \n\0"
        c_fmt = Constant(ArrayType(IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
        global_fmt = GlobalVariable(self.module, c_fmt.type, name=ret_reg('fstr'))
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(self.printf, [fmt_arg, value])

    def emit_print_str(self, source):
        value=self.temps[source]
        voidptr_ty = IntType(8).as_pointer()
        fmt = "%s \n\0"
        c_fmt = Constant(ArrayType(IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
        num = ret_reg('fstr')
        global_fmt = GlobalVariable(self.module, c_fmt.type, name=num)
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(self.printf, [fmt_arg, value])

    def emit_call_func(self, funcname, *args):
        target = args[-1]
        func = self.globals[funcname]
        argvals = [self.temps[name] for name in args[:-1]]
        self.temps[target] = self.builder.call(func, argvals)

    def emit_parm_integer(self, name, num):
        var = self.builder.alloca(integer_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

    def emit_parm_float(self, name, num):
        var = self.builder.alloca(float_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

    def emit_parm_bool(self, name, num):
        var = self.builder.alloca(bool_type, name=name)
        self.builder.store(self.function.args[num], var)
        self.locals[name] = var

    def emit_return_integer(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_float(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_bool(self, source):
        self.builder.store(self.temps[source], self.locals['return'])
        self.branch(self.exit_block)

    def emit_return_void(self):
        self.branch(self.exit_block)

    def emit_prived_float(self, source, target):
        self.temps[target] = self.builder.sitofp(self.temps[source], DoubleType(), name=target)


class GenerateBlocksLLVM(BlockVisitor):

    def __init__(self, generator):
        self.gen = generator

    def perebor(self, elem):
        for i in range(len(elem)):
            if elem[i][0] == 'block_while':
                self.visit_WhileBlock(elem[i+1])
            elif elem[i][0] == 'block_if':
                self.visit_IfBlock(elem[i+1])
            elif elem[i-1][0] == 'block_if' or elem[i-1][0] == 'block_while':
                continue
            # elif i == len(elem)-1:
            #     break
            elif elem[i][0] == 'break':
                self.gen.branch(br[len(br)-1])
                return
            elif elem[i][0] == 'continue':
                self.gen.branch(con[len(con)-1])
                return
            else:
                if type(elem[i]) == tuple and len(elem[i]) <= 4:
                    self.visit_BasicBlock([elem[i]])
                elif len(elem[i]) != tuple:
                    self.visit_BasicBlock(elem[i])


    def generate_function(self, func):
        parm = []
        name = func[0][1]
        if func[0][0] == 'function':
            typ = func[0][len(func[0])-1]
        else:
            typ = 'void'
        if len(func[0]) == 3:
            parm = []
        else:
            for i in range(2, len(func[0])-1):
                parm.append(func[0][i])
        self.gen.start_function(name, typ, parm)
        if name != '_main':
            if func[0][1] != '_init':
                self.visit_BasicBlock(func[1])
                self.visit_BasicBlock(func[2])
                self.perebor(func[3])
                self.gen.terminate()
            else:
                self.visit_BasicBlock(func)
                self.gen.terminate()
        else:
            self.perebor(func[1])
            self.gen.terminate()
        # return self.generator.function

    def visit_BasicBlock(self, func):
        self.gen.generate_code(func)

    def visit_IfBlock(self, block):
        q = block[0][len(block[0])-1][len(block[0][len(block[0])-1])-1]
        self.gen.generate_code(block[0])
        tblock = self.gen.add_block("tblock")
        fblock = self.gen.add_block("fblock")
        endblock = self.gen.add_block("endblock")
        self.gen.cbranch(q, tblock, fblock)
        self.gen.set_block(tblock)
        self.perebor(block[1])
        self.gen.branch(endblock)
        self.gen.set_block(fblock)
        self.gen.branch(endblock)
        self.gen.set_block(endblock)

    def visit_WhileBlock(self, elem):
        test_block = self.gen.add_block("whiletest")
        self.gen.branch(test_block)
        self.gen.set_block(test_block)
        self.gen.generate_code(elem[0])
        q = elem[0][len(elem[0])-1][len(elem[0][len(elem[0])-1])-1]
        loop_block = self.gen.add_block("loop")
        after_loop = self.gen.add_block("afterloop")
        self.gen.cbranch(q, loop_block, after_loop)
        con.append(test_block)
        br.append(after_loop)
        self.gen.set_block(loop_block)
        self.perebor(elem[1])
        self.gen.branch(test_block)
        self.gen.set_block(after_loop)
        con.pop()
        br.pop()

def compile_llvm(source):

    import Tablsimv
    a = Tablsimv.start()
    generator = GenerateLLVM()
    blockgen = GenerateBlocksLLVM(generator)
    for i in range(len(source)):
        # print(('FUNC %s' % source[i][0][1],))
        blockgen.generate_function(source[i])
    generatorss = str(generator.module)
    with open('llvm.ll', 'wb') as f:
        f.write(generatorss.encode('utf-8'))
    return str(generator.module)


def main():
    import sys
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m gone.llvmgen filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    llvm_code = compile_llvm(source)
    print(llvm_code)

if __name__ == '__main__':
    import sys
    import Parser
    import Tablsimv
    import test

    text = open(sys.argv[1]).read()
    a = Tablsimv.start()
    tabl_simv = {}
    Tablsimv.glob_var(tabl_simv)
    Tablsimv.fp_var(tabl_simv)
    tb = tabl_simv
    tac = test.tac(a)
    code_gen = compile_llvm(tac)

