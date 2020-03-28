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
from util import LCG
from FCFS import *
from SJF import *
from SRT import *
from RR import *


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
        
        p.arrival_time *= 1000 # in ms
        p.action_exit = p.arrival_time
        p.action = Action.new

        procsList.append(p)

    # assign CPU burst and I/O block count
    for p in procsList:
        p.burst_time = [0] * int(lcg.drand48() * 100) + 1 # [1, 100]
        p.block_time = [0] * (len(p.burst_time) - 1)

    # assign CPU burst and I/O block time
    for p in procsList:
        for i in range(p.block_time):
            # CPU burst
            p.burst_time[i] = math.ceil(-math.log(lcg.drand48()) / lambda_)
            while (p.burst_time[i] > bound):
                p.burst_time[i] = math.ceil(-math.log(lcg.drand48()) / lambda_)

            # I/O block
            p.block_time[i] = math.ceil(-math.log(lcg.drand48()) / lambda_)
            while (p.block_time[i] > bound):
                p.block_time[i] = math.ceil(-math.log(lcg.drand48()) / lambda_)
            
            p.burst_time[i] *= 1000 # in ms
            p.block_time[i] *= 1000
        
        # last CPU burst
        p.burst_time[-1] = math.ceil(-math.log(lcg.drand48()) / lambda_)
        while (p.burst_time[-1] > bound):
            p.burst_time[-1] = math.ceil(-math.log(lcg.drand48()) / lambda_)
        p.burst_time[-1] *= 1000

    # start simulation
