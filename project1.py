"""
This the spring 2020 CSCI-4210's project 1, project topic is CUP scheduling
    simulation. Scheduling algorithm include first come first served, 
    shortest job first, shortest remaining time, and round robin. 
The initial focus will be on processes, assumed to be resident in memory, 
    waiting to use the CPU. Memory and the I/O subsystem will not be covered 
    in depth in this project.
    
Author
    Zhihao Deng (dengz5@rpi.edu)
    <YOUR NAME>

Last modifly
    March 3, 2020
"""

import sys
import math
from FCFS import *
from SJF import *
from SRT import *
from RR import *


class Process:
    def __init__(self, name: str):
        self.name = name
        self.arrival_time = 0  # process arrival time, in MILLISECONDS

        # use setattr(object, name, value)

        
"""
Linear congruential generator, generate random numbers

Algorithm is inherited from POSIX
"""


class LCG:
    def __init__(self):
        self.seed = 0

    # initialize seed, detail implementation see man srand48
    def srand48(self, seedval: int):
        self.seed = ((seedval & 0xFFFFFFFF) << 16) | 0x330E

    # get random number, detail implementation see man drand48
    def drand48(self) -> float:
        self.seed = (0x5DEECE66D * self.seed + 0xB) & 0xffffffffffff
        return float(self.seed / 0x1000000000000)


if __name__ == "__main__":
    if len(sys.argv) < 8:
        print("ERROR: insufficient arguments", file=sys.stderr, end="")
        sys.exit(1)

    seed = 0        # pseudo-random generator's seed
    lambda_ = 0.0   # it uses in exponential distribution
    bound = 0       # upper bound for valid pseudo-random numbers
    procs = 0       # process count
    t_cs = 0        # context switch time in ms
    alpha = 0.0     # alpah for exponential averaging
    t_slice = 0     # time slice in ms
    add_end = True  # define whether processes are added to the end or the beginning of the ready queue

    try:
        seed = int(sys.argv[1])
        lambda_ = float(sys.argv[2])
        bound = int(sys.argv[3])
        procs = int(sys.argv[4])
        t_cs = int(sys.argv[5])
        alpha = float(sys.argv[6])
        t_slice = int(sys.argv[7])
        if len(sys.argv) > 8:
            add_end = sys.argv[8] == "END"
    except Exception:
        # print("ERROR: invalid arguments", file=sys.stderr, end="")
        print("ERROR: nice try", file=sys.stderr, end="")
        sys.exit(1)

    lcg = LCG()
    lcg.srand48(seed)

    # create process
    # !!! procsList is shared amount all operation, DO NOT modify the list
    procsList = []
    for shift in range(procs):
        p = Process(chr(65 + shift))

        p.arrival_time = math.floor(-math.log(lcg.drand48()) / lambda_)
        while (p.arrival_time > bound):
            p.arrival_time = math.floor(-math.log(lcg.drand48()) / lambda_)

        procsList.append(p)
    
    print(procsList[0].arrival_time)

    # start simulation
