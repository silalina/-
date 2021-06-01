import llvm
import Tablsimv
import test
import Parser
import run

def start():
    f = open('lex.txt')
    parser = Parser.build_tree(f.read())
    vetv = parser.tree()
    return vetv

a=start()

tabl_simv = {}
Tablsimv.glob_var(tabl_simv)
Tablsimv.fp_var(tabl_simv)
test = test.tac(a)
code_gen=llvm.compile_llvm(test)
run.run(code_gen)