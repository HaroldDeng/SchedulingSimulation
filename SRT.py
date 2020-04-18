"""
Shortest remaining time, when a process arrives, before it enters the ready
    queue, if it has a CPU burst time that is less than the remaining time of
    the currently running process, a preemption occurs. When such a preemption
    occurs, the currently running process is added back to the ready queue.

Author
    Zhihao Deng (dengz5@rpi.edu)

"""
import sys
import copy
import math
import time
from util import Action, Process


class SRT:
    def __init__(self, procs: [Process], alpha: int, t_cs: int):
        self.endedQueue = []          # processes in terminated state
        self.readyQueue = []          # processes in ready state
        self.clock = 0                # in ms
        self.alpha = alpha
        self.t_cs = t_cs

        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(procs)

    """
        Core algorithm of SRT implementation.
    """

    def simulate(self):
        #  print all processes
        for p in self.actionQueue:
            print(
                "Process {:s} [NEW] (arrival time {:d} ms) {:d} CPU bursts (tau {:d}ms)".format(
                    p.name, p.arrival_time, len(p.burst_time), p.tau))
            p.action_enter = p.action_leave = p.arrival_time
        print("time 0ms: Simulator started for SRT [Q <empty>]")

        stop = len(self.actionQueue)
        while len(self.endedQueue) < stop:
            interest = [
                p for p in self.actionQueue if self.clock == p.action_enter]
            
            interest.sort(key=self.__sort_by_action)


    """
    print readyQueue
    """

    def printReady(self):
        print("[Q", end="")
        if len(self.readyQueue) == 0:
            print(" <empty>", end="")
        else:
            for p in self.readyQueue:
                print(" " + p.name, end="")
        print("]")

    """ 
    sort order
        (a) CPU burst completion
        (b) I/O burst completion(i.e., back to the ready queue)
        (c) new process arrival
        If ties still happens, break tie with ID order
    """

    def __sort_by_action(self, proc: Process):
        if proc.action == Action.burst:
            return ord(proc.name[0] - 65)
        elif proc.action == Action.new:
            return ord(proc.name[0]) - 65 + 26
        elif proc.action == Action.block:
            return ord(proc.name[0]) - 65 + 26 * 2
        else:
            return ord(proc.name[0]) - 65 + 26 * 3

    # sort actionQueue by action_exit
    def _sort(self):

        def __sort_by_remain(proc: Process):
            return proc.remain - 0.99 + float(ord(proc.name[0]) - 65) / 100.0

        # self.actionQueue.sort(key=__sort_by_end)
        self.readyQueue.sort(key=__sort_by_remain)
