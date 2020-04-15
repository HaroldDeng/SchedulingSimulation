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
from util import Action, Process


class SRT:
    def __init__(self, procs: [Process], tau0: int):
        self.endedQueue = []          # processes in terminated state
        self.readyQueue = []          # processes in ready state
        self.clock = 0                # in ms
        self.tau = tau0                # in ms

        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(procs)

    def simulate(self):
        # print all processes
        for p in self.actionQueue:
            print(
                "Process {:s} [NEW] (arrival time {:d} ms) {:d} CPU bursts".format(
                    p.name, p.arrival_time, len(p.burst_time)
                ))
        print("time 0ms: Simulator started for SRT [Q <empty>]")
        self._sort()

        retVal = self.resume()
        while retVal[0] != None:
            print("time {:d}ms: Process {:s} (tau {d}ms)".format(
                self.clock, retVal[0].name, self.tau), end="")
            if retVal[0].action == Action.new:
                # new process arrived
                print("arrived added to ready queue ", end="")

            elif retVal[0].action == Action.ready:
                # process ready for CPU burst
                print("started using the CPU for {:d}ms burst".format(
                    retVal[0].burst_time[retVal[0].burst_index]), end="")

            elif retVal[0].action == Action.running:
                if retVal[1] != None:
                    # CPU bursting process being preempted
                    pass
                else:
                    pass
            retVal = self.resume(retVal[0])

            # print readyQueue
            print("[Q")
            if len(self.readyQueue) == 0:
                print(" <empty>")
            else:
                for p in self.readyQueue:
                    print(" " + p.name, end="")
            print("]")

    """
        Core algorithm of SRT implementation. On start, pros should be None, 
            after start, pros should be the first element of last returned 
            value.

        @param pros input process.
        @return a Process list with list length is 2
            [None, None] if actionQueue is empty
            [P1, P2] if Process P1 is preempted by Process P2
            [P1, None] otherwise
    """

    def resume(self, pros: Process = None) -> [Process]:
        retVal = [None, None]

        if pros == None:
            pass
        elif pros.action == Action.new:
            pros.action = Action.ready
            self.readyQueue.append(pros)
        elif pros.action == Action.ready:
            pros.action = Action.running
            pros.action_exit = self.clock + pros.burst_time[pros.burst_index]
            self.actionQueue.append(pros)
        elif pros.action == Action.running:
            if pros.burst_index == len(pros.burst_time) - 1:
                pros.action = Action.terninated
                self.endedQueue.append(pros)
            else:
                pros.action = Action.blocked
                self.actionQueue.append(pros)

            pros.burst_index += 1
        elif pros.action == Action.blocked:
            # find CPU bursting process
            btProc = [x for x in self.actionQueue if x.action ==
                      Action.running][0]

            # if remain burst time is greater than I/O ended
            #     process burst time, premmption
            if btProc.action_exit - self.clock > pros.burst_time[pros.burst_index]:
                # remove CPU bursting process from CPU
                self.actionQueue.remove(btProc)
                self.readyQueue.append(btProc)
                # updates
                btProc.preempt_count += 1
                btProc.burst_time[btProc.burst_index] = btProc.action_exit - self.clock
                btProc.action = Action.ready

                # assign new process to CPU
                pros.action = Action.running
                pros.action_exit = self.clock + \
                    pros.burst_time[pros.burst_index]
                self.actionQueue.append(pros)

                retVal[1] = btProc
            else:
                pros.action = Action.ready
                self.readyQueue.append(pros)

            pros.block_index += 1

        else:
            # error
            pass

        if len(self.actionQueue) > 0:
            self._sort()
            retVal[0] = self.actionQueue.pop(0)
        return retVal

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
