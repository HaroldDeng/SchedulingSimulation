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
        print("time 0ms: Simulator started for SRT [Q <empty>]")
        self._sort()

        proc = self.actionQueue.pop(0)
        btProc = None  # bursting process
        self.clock = proc.action_exit

        while(proc != None):

            if proc.action == Action.enter_CPU:
                proc.action = Action.running
                proc.action_exit = self.clock + (self.t_cs >> 1)

            elif proc.action == Action.leave_CPU:
                proc.action = Action.ready
                proc.action_exit = self.clock + (self.t_cs >> 1)
                btProc = None
                if proc.remain == 0:
                    self.readyQueue.append(btProc)
                else:
                    self.readyQueue.append(0, btProc) # preempted process

            elif proc.action == Action.new:
                # process arrive
                print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                    self.clock, proc.name, proc.tau), end="")
                print("arrived; added to ready queue ", end="")
                proc.action = Action.ready
                proc.remain = proc.burst_time[0]
                self.readyQueue.append(proc)
                self.printReady()

            elif proc.action == Action.ready:
                # process ready for CPU burst
                print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                    self.clock, proc.name, proc.tau), end="")
                print("started using the CPU with {:d}ms burst remaining ".format(
                    proc.action_remain), end="")
                proc.action = Action.enter_CPU
                proc.action_exit = self.clock

                self.actionQueue.append(proc)
                self.printReady()

            elif proc.action == Action.running:
                if len(proc.burst_time) - proc.index == 1:
                    # no burst left
                    print("terminated ", end="")
                    proc.action = Action.terninated
                    self.endedQueue.append(proc)
                else:
                    print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                        self.clock, proc.name, proc.tau), end="")

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

                    proc.action_exit = self.clock + \
                        proc.block_time[proc.index] + (self.t_cs >> 1)
                    print("time {:d}ms: Process {:s} switching out of CPU; ".format(
                        self.clock, proc.name), end="")
                    print("will block on I/O until time {:d}ms ".format(
                        proc.action_exit), end="")
                    proc.action = Action.blocked
                    self.actionQueue.append(proc)

                self.printReady()

            elif proc.action == Action.blocked:
                print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                    self.clock, proc.name, proc.tau), end="")
                proc.index += 1
                btProc.action = Action.leave_CPU

                # if remain burst time is greater than I/O ended
                #     process burst time, preemption
                if btProc != None and btProc.action_exit - self.clock > proc.burst_time[proc.index]:
                    print("completed I/O; preempting {:s} ".format(btProc.name),
                          end="")

                    # update bursting process
                    btProc.preempt_count += 1
                    btProc.remain = btProc.action_exit - self.clock
                    self.readyQueue.insert(0, btProc)

                else:
                    # no preemption
                    print("completed I/O; added to ready queue ", end="")
                    btProc.remain = 0

            else:
                # error
                print("ERROR: unknown action on SRT", file=sys.stderr, end="")
                return

            if len(self.actionQueue) > 0:
                self._sort()
                proc = self.actionQueue.pop(0)
                self.clock = proc.action_exit
            elif len(self.readyQueue) > 0:
                proc = self.readyQueue.pop(0)
                self.clock += self.t_cs >> 1
            else:
                proc = None
        print("time {:d}ms: Simulator ended for SJF [Q <empty>]".format(self.clock))

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
            if proc.action == Action.running:
                return proc.action_exit - 0.99 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.new:
                return proc.action_exit - 0.8 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.blocked:
                return proc.action_exit - 0.6 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.leave_CPU or proc.action == Action.preemp_CPU:
                return proc.action_exit - 0.4 + float(ord(proc.name[0]) - 65) / 100.0
            else:
                return proc.action_exit

        self.actionQueue.sort(key=__compare)
