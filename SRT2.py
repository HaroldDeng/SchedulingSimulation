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
        self.flag = False             # indicate of preemption happening

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
        print("time 0ms: Simulator started for SRT [Q <empty>]")
        self._sort()

        proc = self.actionQueue.pop(0)
        btProc = None  # bursting process or the process about to entering CPU

        while(proc != None):

            if proc.action == Action.new:
                # process arrive
                proc.action = Action.ready
                proc.remain = proc.burst_time[0]
                        
                self.readyQueue.append(proc)

                print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                    self.clock, proc.name, proc.tau), end="")
                print("arrived; added to ready queue ", end="")
                self.printReady()

            elif proc.action == Action.ready:
                # process ready for CPU burst
                proc.action = Action.burst
                proc.action_enter = self.clock
                proc.action_leave = self.clock + proc.remain
                self.actionQueue.append(proc)

                print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                    self.clock, proc.name, proc.tau), end="")
                print("started using the CPU with {:d}ms burst remaining ".format(
                    proc.remain), end="")
                self.printReady()

            elif proc.action == Action.burst:
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
                        print("completed a CPU burst; 1 burst to go ", end="")
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

                    proc.action = Action.block
                    proc.action_enter = self.clock + (self.t_cs >> 1)
                    proc.action_leave = proc.action_enter + \
                        proc.block_time[proc.index]
                    self.actionQueue.append(proc)

                    print("time {:d}ms: Process {:s} switching out of CPU; ".format(
                        self.clock, proc.name), end="")
                    print("will block on I/O until time {:d}ms ".format(
                        proc.action_exit), end="")

                self.printReady()

            elif proc.action == Action.block:
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
                    print("completed I/O; added to ready queue ", end="")
                    self.printReady()
                else:
                    # if remain burst time is greater than I/O ended
                    #     process burst time, preemption
                    # take bursting process out of CPU, then insert new process
                    btProc.action = Action.preempted
                    btProc.action_enter = self.clock
                    btProc.action_leave = self.clock + (self.t_cs >> 1)
                    self.actionQueue.remove(btProc)
                    proc.action_enter = self.clock + (self.t_cs >> 1)
                    proc.action_leave = self.clock + self.t_cs
                    self.actionQueue.append(proc)
                    print("completed I/O; preempting {:s} ".format(btProc.name),
                          end="")
                    self.printReady()

            elif proc.action == Action.preempted:
                    proc.preempt_count += 1
                    # preemption process is on index 0
                    self.readyQueue.append(1, proc)
                    btProc = None
                    # keep process's action as preempted
            else:
                # error
                print("ERROR: invalid action on SRT", file=sys.stderr, end="")
                return

            time.sleep(1)
            # retrive process that approach to interest event
            self._sort()
            if btProc == None and len(self.readyQueue) > 0 and len(self.actionQueue) > 0:
                if self.readyQueue[0].action_leave < self.actionQueue[0].action_leave:
                    # if CPU is empty, load process
                    proc = self.readyQueue.pop(0)
                    if proc.action != Action.preempted:
                        proc.remain = proc.burst_time[proc.index]
                    self.actionQueue.append(proc)
                else:
                    proc = self.actionQueue.pop(0)
                
                proc.action = Action.ready
                proc.action_enter = self.clock
                proc.action_leave = self.clock + (self.t_cs >> 1)
                self.clock = proc.action_leave

            elif len(self.actionQueue) > 0:
                proc = self.actionQueue.pop(0)
                self.clock = proc.action_leave
            else:
                proc = None
        print(
            "time {:d}ms: Simulator ended for SJF [Q <empty>]".format(self.clock))

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

    # sort actionQueue by action_exit
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
