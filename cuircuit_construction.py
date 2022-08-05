from qiskit import *
from qiskit.providers.aer import QasmSimulator
from mixers import *

pstp = PauliStringTP(excludeI=True)

def construct_test(h, x, y):
    simulator = QasmSimulator()
    circuit = QuantumCircuit(x)
    circuit.cx(0,1)
    circuit.cx(1,2)

    compiled_circuit = transpile(circuit, simulator)
    circuit.draw()

    return circuit

def cc(circuit, H, cnots, qlist=[]):
    #circuit: takes a circuit as a parameter
    #qlist: qubits that we are going to apply on the circuit
    #H: simplifyed string representation of H done with HtoString
    #cnots: the number of cnots needed to create the circuit

    t_list, p_list = clean_up_pauli_reprecentation(H)
    if len(t_list) != len(p_list):
        print("cant generate qaoa since there is not enough values in t_list and p_list")
        return circuit

    depth = 2*(len(p_list)-1)

    #raise exception if not qlist
    if not isinstance(qlist, list):
        raise NotImplementedError()

    if not qlist:
        for i in range(cnots):
            qlist.append(i)
        qlist.append(cnots)

    cnots -= 1
    #simulator = QasmSimulator()

    for index in range(len(t_list)):
        #U stage
        #pstp.get_items_PS(p_list[index])
        #print(pstp.items)

        #TODO: check for instances of I in bitstring

        circuit.barrier()
        circuit = find_u(circuit, p_list[index], qlist)

        #cnot gate generation stage
        #circuit.cx(range(0,cnots-1,1), range(1,cnots,1))
        circuit, cx_list = construct_cnots(circuit, p_list[index], qlist)
        #create rz gate with (2T) as param
        circuit.rz(2*t_list[index], cnots-1)
        #circuit.cx(range(cnots-2,-1, -1), range(cnots-1, 0, -1))
        #circuit = construct_cnots(circuit, p_list, qlist)
        circuit = constrct_cnots_from_list(circuit, cx_list)

        #U dgr stage
        circuit = find_u_dgr(circuit, p_list[index], qlist)
    print(circuit.draw())


    return circuit

def find_u(circuit, paulistring, qlist):
    try:
        for idx, pauli in enumerate(paulistring):
            if pauli == 'X':
                circuit.h(qlist[idx])
            elif pauli == 'Y':
                circuit.s(qlist[idx])
                circuit.h(qlist[idx])
        return circuit
    except:
        raise ValueError("values not found")

#close to find_u except in the Y case where H and S is switch around
#plus S is substituted with S dagger
def find_u_dgr(circuit, paulistring, qlist):
    try:
        for idx, pauli in enumerate(paulistring):
            if pauli == 'X':
                circuit.h(qlist[idx])
            elif pauli == 'Y':
                circuit.h(qlist[idx])
                circuit.sdg(qlist[idx])
        return circuit
    except:
        raise ValueError("values not found")


def clean_up_pauli_reprecentation(pauli_string):
    little_t_list = []
    p_list = []
    pauli_list = pauli_string.split()

    for item in pauli_list:
        try:
            x = float(item)
            little_t_list.append(x)
        except ValueError:
            p_list.append(item)

    return little_t_list, p_list

def calculate_cnots(circuit, bitstrings, qbitlist, downwards=True):
    print("Bitstring: ",bitstrings)
    print("qbitlist: ", qbitlist)

    #TODO: currently only looking at full string while we should itterate over all characters in string and add accordingly
    if downwards:
        for index, characters in enumerate(bitstrings):
            #TODO: continue here
            for c_index, character in enumerate(characters):
                print("index: ", index)
                print("character: ", character)
                if character == 'I' or (c_index+1) == len(characters):
                    continue
                else:
                   circuit.cx(qbitlist[c_index], qbitlist[c_index+1])
    else:
        for index, characters in enumerate(reversed(bitstrings)):

            for c_index, character in characters:
                if character == 'I' or (c_index+1) == len(characters):
                    continue
                else:
                   circuit.cx(qbitlist[c_index], qbitlist[c_index+1])

    return circuit

def construct_cnots(circuit, bitstring, qbitlist):
    cx_list = []
    print(bitstring)

    for index, character in enumerate(bitstring):
        if (index+1)>= len(bitstring) or character == 'I':
            continue
        else:
            circuit.cx(qbitlist[index], qbitlist[index+1])
            cx_list.append((qbitlist[index], qbitlist[index+1]))


    return circuit, cx_list

def constrct_cnots_from_list(circuit, cx_list):

    while cx_list:
        curr = cx_list.pop()
        circuit.cx(curr[0], curr[1])

    return circuit









