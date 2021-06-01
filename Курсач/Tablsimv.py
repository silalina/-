import Parser

def start():
    f = open('lex.txt')
    parser = Parser.build_tree(f.read())
    vetv = parser.tree()
    return vetv

a=start()
var = []
tabl_simv = {}
dict1 = {}
# print(a)
# print(a[2].parts[0].parts[5].parts[0].parts[1])


def glob_var(tabl_simv):
    dict1 = {}
    mas_id = []
    vremenno = []
    if (a[0] != None):
        for i in range(0, len(a[0].parts[0].parts)):
            for j in range(0, len(a[0].parts[0].parts[i].parts)):
                if a[0].parts[0].parts[i].parts[j]!='real' and a[0].parts[0].parts[i].parts[j]!='integer':
                    mas_id.append(a[0].parts[0].parts[i].parts[j])
                else:
                    for k in range(0, len(mas_id)):
                        vremenno.append(mas_id[k])
                        if a[0].parts[0].parts[i].parts[j]=='integer':
                            vremenno.append('integer')
                        else:
                            vremenno.append('real')
                        dict1.update({vremenno[0]:vremenno[1]})
                        vremenno = []
                    mas_id=[]
                    vremenno = []
        tabl_simv["global"] = dict1
        dict1 = {}
    return tabl_simv

def fp_var(tabl_simv):
    mas_id = []
    vremenno = []
    dict1 = {}
    if (a[1].parts[0] != None):
        for q in range(0, len(a[1].parts)):
            if a[1].parts[q].type == 'function':
                opred = 3
                mas_id.append(a[1].parts[q].parts[0])
                mas_id.append(a[1].parts[q].parts[2].parts[0])
                dict1.update({mas_id[0]:mas_id[1]})
                mas_id = []
            else:
                opred = 2
            for i in range(0, len(a[1].parts[q].parts[1].parts)):
                for j in range(0, len(a[1].parts[q].parts[1].parts[i].parts)):
                    if a[1].parts[q].parts[1].parts[i].parts[j]!='real' and a[1].parts[q].parts[1].parts[i].parts[j]!='integer':
                        mas_id.append(a[1].parts[q].parts[1].parts[i].parts[j])
                    else:
                        for k in range(0, len(mas_id)):
                            vremenno.append(mas_id[k])
                            if a[1].parts[q].parts[1].parts[i].parts[j]=='integer':
                                vremenno.append('integer')
                            else:
                                vremenno.append('real')
                            dict1.update({vremenno[0]:vremenno[1]})
                            vremenno = []
                        mas_id=[]
            if (a[1].parts[q].parts[opred].parts[0] != None):
                for i in range(0, len(a[1].parts[q].parts[opred].parts[0].parts)):
                    for j in range(0, len(a[1].parts[q].parts[opred].parts[0].parts[i].parts)):
                        if a[1].parts[q].parts[opred].parts[0].parts[i].parts[j]!='real' and a[1].parts[q].parts[opred].parts[0].parts[i].parts[j]!='integer':
                            mas_id.append(a[1].parts[q].parts[opred].parts[0].parts[i].parts[j])
                        else:
                            for k in range(0, len(mas_id)):
                                vremenno.append(mas_id[k])
                                if a[1].parts[q].parts[opred].parts[0].parts[i].parts[j]=='integer':
                                    vremenno.append('integer')
                                else:
                                    vremenno.append('real')
                                dict1.update({vremenno[0]:vremenno[1]})
                                vremenno = []
                            mas_id=[]
            tabl_simv[a[1].parts[q].parts[0]] = dict1
            dict1 = {}
            mas = []
    return tabl_simv

def print_table(table):
    for key, value in table.items():
        print(key, value)
        print()

glob_var(tabl_simv)
fp_var(tabl_simv)
# print_table(tabl_simv)


