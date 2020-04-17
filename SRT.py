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
        # print all processes
        for p in self.actionQueue:
            print(
                "Process {:s} [NEW] (arrival time {:d} ms) {:d} CPU bursts".format(
                    p.name, p.arrival_time, len(p.burst_time)))
        print("time 0ms: Simulator started for SRT [Q <empty>]")
        self._sort()

        proc = self.actionQueue.pop(0)
        self.clock = proc.action_exit

        while proc != None:
            # header
            print("time {:d}ms: Process {:s} ".format(
                self.clock, proc.name), end="")

            if proc.action == Action.new:
                print("(tau {:d}ms) ".format(proc.tau), end="")
                # new process arrived
                print("arrived added to ready queue ", end="")
                proc.action = Action.ready
                self.readyQueue.append(proc)

                # TODO, check if running is empty

            elif proc.action == Action.ready:
                print("(tau {:d}ms) ".format(proc.tau), end="")
                # process ready for CPU burst
                print("started using the CPU for {:d}ms burst ".format(
                    proc.burst_time[proc.index]), end="")
                proc.action = Action.running
                proc.action_exit = self.clock + proc.burst_time[proc.index]
                self.actionQueue.append(proc)

            elif proc.action == Action.running:
                if len(proc.burst_time) - proc.index == 1:
                    # no burst left
                    print("terminated ", end="")
                    proc.action = Action.terninated
                    self.endedQueue.append(proc)
                    self.clock += self.t_cs >> 1
                else:
                    print("(tau {:d}ms) ".format(proc.tau), end="")
                    if len(proc.burst_time) - proc.index == 2:
                        # 1 burst left
                        print("completed a CPU burst; 1 bursts to go ", end="")
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

            elif proc.action == Action.blocked:
                # find CPU bursting process
                btProc = None
                if len(self.actionQueue) > 0:
                    btProc = [x for x in self.actionQueue if x.action ==
                              Action.running][0]

                # if remain burst time is greater than I/O ended
                #     process burst time, preemption
                if btProc != None and btProc.action_exit - self.clock > proc.burst_time[proc.index]:
                    print("completed I/O; preempting {:s} ".format(btProc.name),
                          end="")
                    # remove CPU bursting process from CPU
                    self.actionQueue.remove(btProc)
                    self.readyQueue.insert(0, btProc)
                    # updates
                    btProc.preempt_count += 1
                    btProc.burst_time[btProc.index] = btProc.action_exit - self.clock
                    btProc.action = Action.ready

                    # assign new process to CPU
                    proc.action = Action.running
                    proc.action_exit = self.clock + proc.burst_time[proc.index] + self.t_cs
                    self.actionQueue.append(proc)

                else:
                    # no preemption
                    print("completed I/O; added to ready queue ", end="")
                    proc.action = Action.ready
                    self.readyQueue.append(proc)

                proc.index += 1

            else:
                # error
                print("ERROR: unknown action on SRT", file=sys.stderr, end="")
                return

            self.printReady()

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
            elif proc.action == Action.blocked:
                return proc.action_exit - 0.34 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.new:
                return proc.action_exit - 0.67 + float(ord(proc.name[0]) - 65) / 100.0
            elif proc.action == Action.ready:
                return proc.action_exit

        self.actionQueue.sort(key=__compare)
