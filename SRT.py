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
    def __init__(self, processes: [Process]):
        self.endedQueue = []          # processes in terminated state
        self.readyQueue = []          # processes in ready state
        self.clock = 0                # in ms

        # processes in state other than ready and terminated
        self.actionQueue = copy.deepcopy(processes)

    def simulate(self):
        pass

    def resume(self, pros: Process) -> [Process]:
        retVal = [None, None]
        if pros.action == Action.new:
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
                # remove bursting process from CPU
                btProc.preempt_count += 1
                btProc.burst_time[btProc.burst_index] = btProc.action_exit - self.clock
                btProc.action = Action.ready
                self.actionQueue.remove(btProc)
                self.readyQueue.append(btProc)

                # replacement start CPU burst
                pros.action = Action.running
                pros.action_exit = self.clock + pros.burst_time[pros.burst_index]
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
