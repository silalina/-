import Tablsimv
import test

ircode = [('parm_integer', 'e', 0), ('parm_integer', 'x', 1), ('parm_integer', 'y', 2), ('parm_integer', 'z', 3), ('parm_float', 'a', 4), ('parm_float', 'b', 5)]

for opcode, *args in ircode:
    print(opcode, *args)
    if hasattr('emit_' + opcode):
        getattr('emit_' + opcode)(*args)


