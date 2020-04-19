import sys
import copy
import math
import time
from util import Action, Process



class FCFS:
    def __init__(self, procs: [Process], alpha: int, t_cs: int):
        self.endedQueue = []          # processes in terminated state
        self.readyQueue = []          # processes in ready state
        self.clock = 0                # in ms
        self.alpha = alpha            # numbers of alphabets(proc)
        self.t_cs = t_cs              #context switch
        self.burst=0                  # total burst time
        self.bts=0                    # total burst number
        self.turnaround=0             # total turnaround time
        self.trs =0                   # total turnaround number
        self.wait=0                   # total wait time
        self.wts=0                    # total wait number
        self.block=0                     # total IO time(block)
        
        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(procs)
        
    def _sort(self):
    
        # (a) CPU burst completion
        # (b) I/O burst completion(i.e., back to the ready queue)
        # (c) new process arrival
        # If ties still happens, break tie with ID order
        def __compare(proc: Process):
            if proc.action == Action.preempted:
                return proc.action_leave - 0.99 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.burst:
                return proc.action_leave - 0.75 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.new:
                return proc.action_leave - 0.5 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.block:
                return proc.action_leave - 0.25 + float(ord(proc.name[0]) - 65) / 100.0
            else:
                return proc.action_leave + float(ord(proc.name[0]) - 65) / 100.0
        self.actionQueue.sort(key=__compare)
    
    def printReady(self):
        print("[Q", end="")
        if len(self.readyQueue) == 0:
            print(" <empty>", end="")
        else:
            for p in self.readyQueue:
                print(" " + p.name, end="")
        print("]")
        
    def simulate(self):
        for p in self.actionQueue:
            self.burst += sum(p.burst_time)
            self.bts += len(p.burst_time)
            self.block += sum(p.block_time)
            print("Process {:s} [NEW] (arrival time {:d} ms) {:d} CPU bursts"
                  .format(p.name, p.arrival_time, self.bts))
        print("time 0ms: Simulator started for FCFS [Q <empty>]")
        self._sort()
        self.readyQueue.append(self.actionQueue.pop(0))
        self.clock = self.readyQueue[0].arrival_time
        proc = self.readyQueue[0]
        proc.action_enter = self.clock
        proc.action_leave = self.clock + (self.t_cs >> 1)        
        proc.remain = proc.burst_time[0]
        
        while(proc!=None):
            if proc.action == Action.new:
                # process arrive
                print("time {:d}ms: Process {:s} "
                      .format(self.clock, proc.name), end="")
                print("arrived; added to ready queue ", end="")
                self.printReady()
                
                proc = self.readyQueue.pop(0)
                proc.action_enter = self.clock
                self.clock += (self.t_cs >> 1)
                proc.action_leave = self.clock   
                proc.remain = proc.burst_time[0]
                proc.action = Action.ready 
                
            elif proc.action == Action.ready:
                # process ready for CPU burst
                proc.remain = proc.burst_time[proc.index]
                proc.action = Action.burst
                proc.action_enter = self.clock
                proc.action_leave = self.clock + proc.remain
                self.actionQueue.append(proc)
                print("time {:d}ms: Process {:s} "
                      .format(self.clock, proc.name), end="")
                print("started using the CPU for {:d}ms burst "
                      .format(proc.remain), end="")
                self.printReady()  
                
                
            elif proc.action == Action.burst:
                print("time {:d}ms: Process {:s} "
                      .format(self.clock, proc.name), end="")
                if len(proc.burst_time) - proc.index == 1:
                    #last burst
                    proc.action = Action.block
                    self.endedQueue.append(proc)
                    print("terminated ", end="")
                    proc=None
                elif len(proc.burst_time) - proc.index == 2:
                    #second last burst without s
                    print("completed a CPU burst; {:d} burst to go "
                          .format(len(proc.burst_time) - proc.index - 1), end="")
                    self.printReady()
                    proc.action = Action.block
                    proc.action_enter = self.clock + (self.t_cs >> 1)
                    proc.action_leave = proc.action_enter + proc.block_time[proc.index]
                    self.actionQueue.append(proc)

                    print("time {:d}ms: Process {:s} switching out of CPU; "
                          .format(self.clock, proc.name), end="")
                    print("will block on I/O until time {:d}ms "
                          .format(proc.action_leave), end="")
                    
                else:
                    print("completed a CPU burst; {:d} bursts to go "
                          .format(len(proc.burst_time) - proc.index - 1), end="")
                    self.printReady()
                    proc.action = Action.block
                    proc.action_enter = self.clock + (self.t_cs >> 1)
                    proc.action_leave = proc.action_enter + proc.block_time[proc.index]
                    self.actionQueue.append(proc)

                    print("time {:d}ms: Process {:s} switching out of CPU; "
                          .format(self.clock, proc.name), end="")
                    print("will block on I/O until time {:d}ms "
                          .format(proc.action_leave), end="")
                self.printReady() 
                
            elif proc.action == Action.block:
                print("time {:d}ms: Process {:s} "
                      .format(self.clock, proc.name), end="")
                
                proc.index += 1 
                proc.action = Action.ready
                self.readyQueue.append(proc)
                # no preemption
                proc.action_enter = self.clock
                proc.action_leave = self.clock  + (self.t_cs >> 1)
                print("completed I/O; added to ready queue ", end="")
                self.printReady()
                proc=None
                
            time.sleep(1)
            self._sort()
            if proc==None and len(self.readyQueue) > 0:
                # if CPU is empty, load process
                proc = self.readyQueue.pop(0)
                proc.action_enter = self.clock
                self.clock += (self.t_cs >> 1)
                proc.action_leave = self.clock 
            elif len(self.actionQueue) > 0:
                self.readyQueue.append(self.actionQueue.pop(0))
                self.clock = self.readyQueue[0].action_leave
                proc = self.readyQueue.pop(0)
                                 
                                 
        self.clock += (self.t_cs >> 1)       
        print("time {:d}ms: Simulator ended for FCFS [Q <empty>]".format(self.clock))