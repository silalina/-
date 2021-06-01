import Tablsimv
import test
import llvm
import run

a = Tablsimv.start()

def pr_tb(tb):
    for key, value in tb.items():
        print(key, value)
        print()

tabl_simv = {}
Tablsimv.glob_var(tabl_simv)
Tablsimv.fp_var(tabl_simv)
tb = tabl_simv
tac = test.tac(a)
code_gen=llvm.compile_llvm(tac)
run.run(code_gen)

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