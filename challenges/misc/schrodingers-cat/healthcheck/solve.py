#!/usr/bin/env python3

import numpy as np
from base64 import b64encode
from qiskit import *
from qiskit.circuit.library import StatePreparation
from qiskit.compiler import transpile
import qiskit.quantum_info as qi

WIRES = 5

# helper functions from challenge
def normalization(msg):
    assert(len(msg) <= WIRES**2)
    state = np.array([ord(c) for c in msg.ljust(2**WIRES, ' ')])
    norm = np.linalg.norm(state)
    state = state / norm
    return (state, norm)

def transform(sv, n):
    legal = lambda c: ord(' ') <= c and c <= ord('~')
    renormalized = [float(i.real)*n for i in sv]
    rn_rounded = [round(i) for i in renormalized]
    if not np.allclose(renormalized, rn_rounded, rtol=0, atol=1e-2):
        print("Your rehydrated statevector isn't very precise. Try adding at least 6 decimal places of precision, or contact the challenge author if you think this is a mistake.")
        print(rn_rounded)
        exit(0)
    if np.any([not legal(c) for c in rn_rounded]):
        print("Invalid ASCII characters.")
        exit(0)
    return ''.join([chr(n) for n in rn_rounded])


def solve_qiskit():
    echo_sv, _ = normalization("echo 'Hello, world!'")
    cat_sv, cat_n = normalization("cat /flag.txt")
    # you can also test that other shell commands work

    circ = QuantumCircuit(WIRES)
    circ.append(StatePreparation(cat_sv, label="sp"), range(WIRES))
    circ.append(StatePreparation(echo_sv, label="inv_sp", inverse=True), range(WIRES))

    # append the origianl StatePreparation to confirm that this works; remove for payload
    #circ.append(StatePreparation(echo_sv), range(WIRES))
    circ = transpile(circ, backend=Aer.get_backend("aer_simulator"), optimization_level=3)
    sv = qi.Statevector.from_instruction(circ)

    # this will be wrong for the payload, because there's no final StatePrep
    #print(transform(sv, cat_n))
    return b64encode(circ.qasm().encode()), cat_n
    #circ.from_qasm_str(circ.qasm())

if __name__ == "__main__":
    print(solve_qiskit())
