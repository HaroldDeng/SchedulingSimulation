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
        self.btProc = None            # bursting process

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
                p for p in self.actionQueue
                if self.clock == p.action_enter or self.clock == p.action_leave]
            if len(interest) > 0:
                interest.sort(key=self.__sort_by_action)
                for proc in interest:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    if proc.action == Action.new:
                        # process arrive
                        proc.action = Action.ready
                        proc.remain = proc.burst_time[0]
                        self.readyQueue.append(proc)
                        self.readyQueue.sort(key=self.__sort_by_remain)
                        print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                            self.clock, proc.name, proc.tau), end="")
                        print("arrived; added to ready queue ", end="")
                        self.printReady()

                    elif proc.action == Action.enter_CPU:
                        # process being push into CPU
                        proc.action = Action.burst
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + (self.t_cs >> 1)
                        if proc.remain == 0:
                            # next burst slice
                            proc.remain = proc.burst_time[proc.index]
                        self.actionQueue.append(proc)
                        self.btProc = proc # assign process

                    elif proc.action == Action.leave_CPU:
                        # process finished CPU burst
                        proc.action = Action.block
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + \
                            proc.block_time[proc.index]
                        self.btProc = None # no bursting process

                    elif proc.action == Action.burst and self.clock == proc.action_enter:
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + proc.remain
                        self.actionQueue.append(proc)
                        print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                            self.clock, proc.name, proc.tau), end="")
                        print("started using the CPU with {:d}ms burst remaining ".format(
                            proc.remain), end="")
                        self.printReady()

                    elif proc.action == Action.burst and self.clock == proc.action_leave:
                        print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                            self.clock, proc.name, proc.tau), end="")
                        if len(proc.burst_time) - proc.index == 1:
                            # no burst left
                            proc.action = Action.terninated
                            self.endedQueue.append(proc)
                            print("terminated ", end="")
                        else:
                            if len(proc.burst_time) - proc.index == 2:
                                # 1 burst left
                                print(
                                    "completed a CPU burst; 1 burst to go ", end="")
                            else:
                                # > 1 bursts left
                                print("completed a CPU burst; {:d} bursts to go ".format(
                                    len(proc.burst_time) - proc.index - 1), end="")
                            self.printReady()

                            # recalculate tau
                            proc.tau = math.ceil(self.alpha * proc.burst_time[proc.index] +
                                                 (1-self.alpha) * proc.tau)
                            print("time {:d}ms: Recalculated tau = {:d}ms for process {:s} ".format(
                                self.clock, proc.tau, proc.name), end="")
                            self.printReady()

                            # leave CPU
                            proc.action = Action.leave_CPU
                            proc.action_enter = self.clock
                            proc.action_leave = self.clock + (self.t_cs >> 1)
                            proc.remain -= self.clock - proc.action_leave
                            self.actionQueue.append(proc)
                            print("time {:d}ms: Process {:s} switching out of CPU; ".format(
                                self.clock, proc.name), end="")
                            print("will block on I/O until time {:d}ms ".format(
                                proc.action_leave + proc.block_time[proc.index]), end="")

                    elif proc.action == Action.block and self.clock == proc.action_leave:
                        print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                            self.clock, proc.name, proc.tau), end="")
                        proc.index += 1
                        proc.action = Action.ready

                        if btProc != None:
                            btProc.remain -= self.clock - btProc.action_enter
                        if btProc == None or btProc.remain > proc.burst_time[proc.index]:
                            # no preemption
                            proc.action_enter = self.clock
                            proc.action_leave = self.clock + (self.t_cs >> 1)
                            proc.remain = proc.burst_time[proc.index]
                            self.readyQueue.append(proc)
                            self.readyQueue.sort(self.__sort_by_remain)
                            print("completed I/O; added to ready queue ", end="")
                            self.printReady()
                        else:
                            # if remain burst time is greater than I/O ended
                            #     process burst time, preemption
                            # take bursting process out of CPU, then insert new process
                            



                    elif proc.action == Action.preempted:
                        # """
                        # sort readyQueue before call
                        # """
                        # def checkPreempt(self):
                        #     if self.btProc != None and len(self.readyQueue) > 0:
                        #         btProc.remain -= self.clock - btProc.action_enter
                        #         if self.readyQueue[0].remain < self.btProc.remain:

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
        elif proc.action == Action.block:
            return ord(proc.name[0]) - 65 + 26
        elif proc.action == Action.new:
            return ord(proc.name[0]) - 65 + 26 * 3
        else:
            return ord(proc.name[0]) - 65 + 26 * 3

    """
    sort order
        remaining time
        If ties still happens, break tie with ID order
    """
    def __sort_by_remain(proc: Process):
        return proc.remain + ord(proc.name[0]) - 65
