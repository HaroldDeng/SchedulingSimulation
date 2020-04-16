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
    def __init__(self, procs: [Process], alpha: int, t_cs: int):
        self.endedQueue = []          # processes in terminated state
        self.readyQueue = []          # processes in ready state
        self.clock = 0                # in ms
        self.alpha = alpha
        self.t_cs = t_cs

        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(procs)

    def simulate(self):
        # print all processes
        for p in self.actionQueue:
            print(
                "Process {:s} [NEW] (arrival time {:d} ms) {:d} CPU bursts".format(
                    p.name, p.arrival_time, len(p.burst_time)))
        print("time 0ms: Simulator started for SRT [Q <empty>]")
        self._sort()

        retVal = self.resume()
        while retVal[0] != None:
            print("time {:d}ms: Process {:s} (tau {:d}ms) ".format(
                self.clock, retVal[0].name, retVal[0].tau), end="")
            if retVal[0].action == Action.new:
                # new process arrived
                print("arrived added to ready queue ", end="")

            elif retVal[0].action == Action.ready:
                # process ready for CPU burst
                print("started using the CPU for {:d}ms burst remaining ".format(
                    retVal[0].burst_time[retVal[0].index]), end="")

            elif retVal[0].action == Action.running:
                # process finished CPU burst

                if len(retVal[0].burst_time) - retVal[0].index == 1:
                    # no burst left
                    print("terminated ", end="")
                else:
                    if len(retVal[0].burst_time) - retVal[0].index == 2:
                        # 1 burst left
                        print("completed a CPU burst; 1 bursts to go ", end="")
                    else:
                        # > 1 bursts left
                        print("completed a CPU burst; {:d} bursts to go ".format(
                            len(retVal[0].burst_time) - retVal[0].index - 1), end="")

                    # recalculate tau
                    retVal[0].tau = self.alpha * \
                        retVal[0].burst_time[retVal[0].index] + \
                        (1-self.alpha) * retVal[0].tau
                    print("time {:d}ms: Recalculated tau = {:d}ms for process {:s} ".format(
                        self.clock, retVal[0].tau, retVal[0].name), end="")
                    self.printReady()

                    print("time {:d}ms: Process {:s} switching out of CPU; will block on I/O until time {:d}ms ".format(
                        self.clock, retVal[0].name,
                        self.clock + self.t_cs >> 1 + retVal[0].block_time[retVal[0].index]), end="")
                    self.printReady()
                
            elif retVal[0].action == Action.blocked:
                if retVal[1] == None:
                    # no preemption
                    print("completed I/O; added to ready queue ", end="")
                else:
                    # retVal[0] preempt retVal[1]
                    print("completed I/O; preempting {:s}".format(retVal[1].name), end="")

            retVal = self.resume(retVal[0])
            self.printReady()

            return

    """
        Core algorithm of SRT implementation. On start, pros should be None, 
            after start, pros should be the first element of last returned 
            value.

        @param pros input process.>
        @return a Process list with list length is 2
            [None, None] if actionQueue is empty
            [P1, P2] if Process P1 is preempting Process P2
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
            pros.action_exit = self.clock + pros.burst_time[pros.index]
            self.actionQueue.append(pros)
        elif pros.action == Action.running:
            if len(pros.burst_time) - pros.index == 1:
                pros.action = Action.terninated
                self.endedQueue.append(pros)
            else:
                pros.action = Action.blocked
                self.actionQueue.append(pros)
        elif pros.action == Action.blocked:
            # find CPU bursting process
            btProc = [x for x in self.actionQueue if x.action ==
                      Action.running][0]

            # if remain burst time is greater than I/O ended
            #     process burst time, preemption
            if btProc.action_exit - self.clock > pros.burst_time[pros.index]:
                # remove CPU bursting process from CPU
                self.actionQueue.remove(btProc)
                self.readyQueue.insert(0, btProc)
                # updates
                btProc.preempt_count += 1
                btProc.burst_time[btProc.index] = btProc.action_exit - self.clock
                btProc.action = Action.ready

                # assign new process to CPU
                pros.action = Action.running
                pros.action_exit = self.clock + pros.burst_time[pros.index]
                self.actionQueue.append(pros)

                retVal[0] = btProc
            else:
                pros.action = Action.ready
                self.readyQueue.append(pros)

            pros.index += 1

        else:
            # error
            pass

        if len(self.actionQueue) > 0:
            self._sort()
            if retVal[0] == None:
                retVal[0] = self.actionQueue.pop(0)
                self.clock = retVal[0].action_exit
            else:
                retVal[1] = self.actionQueue.pop(0)
                self.clock = retVal[1].action_exit
        return retVal

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
