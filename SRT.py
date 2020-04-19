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
        self.alpha = alpha
        self.t_cs = t_cs
        self.clock = 0                # in ms
        self.btProc = None            # process in CPU including enter and leave state
        self.ptProc = None            # preempting process

        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(procs)

    """
        Core algorithm of SRT implementation.
    """

    def simulate(self) -> (int, int, int, int, int):
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
            interest.sort(key=self.__sort_by_action)
            if self.clock == 2714:
                tmp = 0

            for proc in interest:

                if proc.action == Action.enter_CPU and self.clock == proc.action_leave:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    # process being push into CPU
                    if proc.remain == 0:
                        # next burst slice
                        proc.remain = proc.burst_time[proc.index]

                    if self.ptProc != None:
                        # preemption, self.ptProc is proc
                        self.readyQueue.remove(self.ptProc)
                        self.readyQueue.append(self.btProc)
                        self.readyQueue.sort(key=self.__sort_by_remain)
                        self.ptProc = None
                    proc.action = Action.burst
                    proc.action_enter = self.clock
                    proc.action_leave = self.clock + proc.remain
                    proc.switch_count += 1
                    self.actionQueue.append(proc)
                    self.btProc = proc

                if proc.action == Action.leave_CPU and self.clock == proc.action_leave:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    # process finished context switch
                    if proc.remain == -1:
                        # terminated
                        proc.action = Action.terninated
                        self.endedQueue.append(proc)
                        self.btProc = None
                    elif proc.remain == 0:
                        # entering I/O time
                        proc.action = Action.block
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + \
                            proc.block_time[proc.index]
                        self.btProc = None
                        self.actionQueue.append(proc)
                    else:
                        # process being preempted
                        self.btProc = Action.ready
                        self.btProc = self.ptProc
                        self.ptProc = None
                        self.readyQueue.append(proc)
                        self.readyQueue.sort(key=self.__sort_by_remain)

                if proc.action == Action.new:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    # process arrive
                    proc.action = Action.ready
                    proc.remain = proc.burst_time[0]
                    self.readyQueue.append(proc)
                    self.readyQueue.sort(key=self.__sort_by_remain)
                    print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                        self.clock, proc.name, proc.tau), end="")
                    print("arrived; added to ready queue ", end="")
                    self.printReady()

                if proc.action == Action.burst and self.clock == proc.action_enter:
                    print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                        self.clock, proc.name, proc.tau), end="")
                    print("started using the CPU with {:d}ms burst remaining ".format(
                        proc.remain), end="")
                    self.printReady()

                    if len(self.readyQueue) > 0:
                        proc2 = self.readyQueue[0]
                        if proc2.tau < proc.tau:
                            # preempting
                            proc.action = Action.leave_CPU
                            proc.action_enter = self.clock
                            proc.action_leave = self.clock + \
                                (self.t_cs >> 1)
                            proc.preempt_count += 1
                            self.actionQueue.remove(proc)
                            proc2.action = Action.enter_CPU
                            proc2.action_enter = self.clock + (self.t_cs >> 1)
                            proc2.action_leave = self.clock + self.t_cs
                            self.ptProc = proc2
                            self.actionQueue.append(proc2)
                            print("time {:d}ms: Process {:s} (tau {:d}ms) will preempt {:s} ".format(
                                self.clock, proc2.name, proc2.tau, proc.name), end="")
                            self.printReady()

                if proc.action == Action.burst and self.clock == proc.action_leave:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    # end of I/O
                    print("time {:d}ms: Process {:s} ".format(
                        self.clock, proc.name), end="")
                    if len(proc.burst_time) == proc.index + 1:
                        # no burst left
                        proc.action = Action.leave_CPU
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + (self.t_cs >> 1)
                        proc.remain = -1
                        self.actionQueue.append(proc)
                        print("terminated ", end="")

                    else:
                        print("(tau {:d}ms) ".format(proc.tau), end="")
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

                        # starting I/O
                        proc.action = Action.leave_CPU
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + (self.t_cs >> 1)
                        proc.remain = 0
                        self.actionQueue.append(proc)
                        print("time {:d}ms: Process {:s} switching out of CPU; ".format(
                            self.clock, proc.name), end="")
                        print("will block on I/O until time {:d}ms ".format(
                            proc.action_leave + proc.block_time[proc.index]), end="")
                    self.printReady()

                if proc.action == Action.block and self.clock == proc.action_leave:
                    self.actionQueue.remove(proc)  # pop from actionQueue
                    print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                        self.clock, proc.name, proc.tau), end="")
                    proc.index += 1
                    proc.action = Action.ready
                    self.readyQueue.append(proc)
                    self.readyQueue.sort(key=self.__sort_by_remain)

                    estmate = -1
                    if self.btProc != None and self.btProc.action == Action.burst:
                        self.btProc.remain -= self.clock - self.btProc.action_enter
                        estmate = self.btProc.tau - \
                            (self.btProc.burst_time[self.btProc.index] -
                             self.btProc.remain)
                    if estmate < proc.tau:
                        # if self.btProc == None or newT < proc.tau or self.btProc.action != Action.burst:
                        # no preemption
                        proc.action_enter = self.clock
                        proc.action_leave = self.clock + (self.t_cs >> 1)
                        proc.remain = proc.burst_time[proc.index]
                        print("completed I/O; added to ready queue ", end="")
                        self.printReady()
                    else:
                        # if remain burst time is greater than I/O ended
                        #     process burst time, preemption
                        # take bursting process out of CPU, then insert new process
                        self.btProc.action = Action.leave_CPU
                        self.btProc.action_enter = self.clock
                        self.btProc.action_leave = self.clock + \
                            (self.t_cs >> 1)
                        self.actionQueue.remove(self.btProc)
                        proc.action = Action.enter_CPU
                        proc.action_enter = self.clock + (self.t_cs >> 1)
                        proc.action_leave = self.clock + self.t_cs
                        self.ptProc = proc
                        self.ptProc.preempt_count += 1
                        self.actionQueue.append(proc)
                        print("completed I/O; preempting {:s} ".format(self.btProc.name),
                              end="")
                        self.printReady()

            # push new process into CPU
            if self.btProc == None and len(self.readyQueue) > 0:
                self.btProc = self.readyQueue.pop(0)
                self.btProc.action = Action.enter_CPU
                self.btProc.action_enter = self.clock
                self.btProc.action_leave = self.clock + \
                    (self.t_cs >> 1)
                self.actionQueue.append(self.btProc)

            # insert new process
            self.clock += 1

        print("time {:d}ms: Simulator ended for SRT ".format(self.clock - 1), end="")
        self.printReady()

        tmp = [sum(x.burst_time) for x in self.endedQueue]
        avg_bt = sum(tmp) / len(tmp)  # average burst time
        tmp = [x.action_leave - x.arrival_time - sum(x.burst_time) - 
            sum(x.block_time) - 2 * x.switch_count * (self.t_cs >> 1)
            for x in self.endedQueue]
        avg_wt = sum(tmp) / len(tmp)  # average wait time
        tmp = [x.action_leave - x.arrival_time for x in self.endedQueue]
        avg_tt = sum(tmp) / len(tmp)  # average turnaround time
        tmp = [x.switch_count for x in self.endedQueue]
        sum_cs = sum(tmp)             # total context switches
        tmp = [x.preempt_count for x in self.endedQueue]
        sum_pp = sum(tmp)             # total preemptions
        return (avg_bt, avg_wt, avg_tt, sum_cs, sum_pp)


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
            return ord(proc.name[0]) - 65 + 26 * 3
        elif proc.action == Action.block:
            return ord(proc.name[0]) - 65 + 26 * 2
        elif proc.action == Action.new:
            return ord(proc.name[0]) - 65 + 26 * 1
        else:
            return ord(proc.name[0]) - 65 + 26

    """
    sort order
        remaining time
        If ties still happens, break tie with ID order
    """

    def __sort_by_remain(self, proc: Process):
        return proc.remain + ord(proc.name[0]) - 65
