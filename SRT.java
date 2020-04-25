import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * A class that represents the First Come First Serve CPU scheduling algorithm
 */
public class SRT extends CPUSchedual {
    public SRT(List<Process> procs, int t_cs, double alpha) {
        readyList = new ArrayList<Process>(procs.size());
        actionList = new ArrayList<Process>(procs.size());
        endedList = new ArrayList<Process>(procs.size());
        fs = new FormatedStdout("SRT", Integer.MAX_VALUE);
        this.t_cs = t_cs;
        this.alpha = alpha;
        clock = 0;

        // deep copy
        Iterator<Process> itr = procs.iterator();
        try {
            while (itr.hasNext()) {
                actionList.add(itr.next().clone());
            }
        } catch (CloneNotSupportedException exc) {
            System.err.print("ERROR: Clone process failed.");
            System.exit(-1);
        }
    }

    @Override
    public double[] simulate() {
        // print all processes
        fs.printAll(actionList);
        System.out.println("time 0ms: Simulator started for SRT [Q <empty>]");
        actionList.sort(new _sortByState());
        // store process that is in load state
        Process btProc = null; // process with LOAD or BURST or UNLOAD state
        while (actionList.size() != 0) {

            // get time from next process
            clock = actionList.get(0).kTime;

            if (clock == 8959) {
                int X = 0;
            }

            while (actionList.size() > 0 && actionList.get(0).kTime == clock) {
                Process proc = actionList.remove(0);
                switch (proc.state) {
                    case NEW:
                        proc.state = States.READY;
                        readyList.add(proc);
                        readyList.sort(new _sortByEstmate());
                        fs.printArrival(clock, proc, readyList);
                        break;

                    case READY:
                        // perpear for load into CPU, load state
                        proc.state = States.LOAD;
                        proc.kTime += t_cs >> 1;
                        actionList.add(proc);
                        btProc = proc;
                        break;

                    case LOAD:
                        // loaded into CPU complete, next state is burst
                        proc.state = States.BURST;
                        proc.kTime += proc.remain;
                        // proc.csCount += 1; // context switch
                        fs.printStartedBurst(clock, proc, readyList);
                        actionList.add(proc);
                        break;

                    case BURST:
                        // burst complete, into unload state
                        proc.state = States.UNLOAD;
                        proc.kTime += t_cs >> 1;
                        proc.remain = 0;
                        if (proc.burstTimes.length - proc.progress == 1) {
                            // process terminated, but unload from CPU first
                            fs.printTerminate(clock, proc, readyList);
                        } else {
                            fs.printEndedBurst(clock, proc, readyList);
                            proc.tau = (int) Math.ceil(alpha * proc.burstTimes[proc.progress] + (1 - alpha) * proc.tau);
                            fs.printReTau(clock, proc, readyList);
                            proc.kTime += proc.blockTimes[proc.progress]; // just for print
                            fs.printStartedBlock(clock, proc, readyList);
                            proc.kTime -= proc.blockTimes[proc.progress];
                        }
                        actionList.add(proc);
                        break;

                    case UNLOAD:
                        // unload from CPU
                        if (proc.remain > 0) {
                            // being preempted
                            proc.state = States.READY;
                            readyList.add(proc);
                            readyList.sort(new _sortByEstmate());
                        } else if (proc.burstTimes.length - proc.progress == 1) {
                            // no more burst to go, process terminate
                            proc.state = States.TERMINATED;
                            endedList.add(proc);
                        } else {
                            // more bursts to go, and not being preempted
                            proc.state = States.BLOCK;
                            proc.kTime += proc.blockTimes[proc.progress];
                            actionList.add(proc);

                        }
                        proc.csCount += 1; // context switch
                        btProc = null;
                        break;

                    case BLOCK:
                        // block complete, no preemption in FCFS
                        proc.state = States.READY;
                        proc.progress += 1;
                        proc.remain = proc.burstTimes[proc.progress];
                        readyList.add(proc);
                        readyList.sort(new _sortByEstmate());
                        // check preemption
                        if (btProc != null && btProc.state == States.BURST) {
                            btProc.remain = btProc.kTime - clock;
                            int estLeft = btProc.tau - btProc.burstTimes[btProc.progress] + btProc.remain;
                            if (estLeft > proc.tau) {
                                // perform preemption
                                btProc.state = States.UNLOAD;
                                btProc.kTime = clock + (t_cs >> 1);
                                fs.printEndedBlock(clock, proc, btProc, readyList);
                            } else {
                                fs.printEndedBlock(clock, proc, null, readyList);
                            }
                        } else {
                            fs.printEndedBlock(clock, proc, null, readyList);
                        }

                        break;

                    default:
                        System.err.println("Error: unexpected state.");
                        System.exit(-1);
                }

                // sort
                actionList.sort(new _sortByState());
            }

            // empty CPU, add new process
            if (readyList.size() > 0) {
                if (btProc == null) {
                    Process tmp = readyList.remove(0);
                    tmp.kTime = clock;
                    actionList.add(tmp);
                    actionList.sort(new _sortByState());
                } else if (btProc != null && btProc.state == States.BURST) {
                    // check if any ready process should preempts bursting process
                    btProc.remain = btProc.kTime - clock;
                    int estLeft = btProc.tau - btProc.burstTimes[btProc.progress] + btProc.remain;
                    Process tmp = readyList.get(0);
                    if (estLeft > tmp.tau) {
                        btProc.state = States.UNLOAD;
                        btProc.kTime = clock + (t_cs >> 1);
                        System.out.printf("time %dms: Process %c (tau %dms) will preempt %c ", clock, tmp.name, tmp.tau,
                                btProc.name);
                        fs.printReady(readyList);
                        actionList.sort(new _sortByState());
                    }
                }
            }
        }

        System.out.printf("time %dms: Simulator ended for SRT ", clock);
        fs.printReady(readyList);

        double retVal[] = new double[5];
        // calRetVal(retVal);
        // System.err.printf("%.3f %.3f %.3f %.0f %.0f", retVal[0], retVal[1],
        // retVal[2], retVal[3], retVal[4]);
        return retVal;
    }
}
