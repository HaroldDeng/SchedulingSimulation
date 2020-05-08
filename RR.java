import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * A class that represents the First Come First Serve CPU scheduling algorithm
 */
public class RR extends CPUSchedual {
    private boolean add_end;
    private int t_slice;

    public RR(List<Process> procs, int t_cs, int t_slice, boolean add_end, int limit) {
        readyList = new ArrayList<Process>(procs.size());
        actionList = new ArrayList<Process>(procs.size());
        endedList = new ArrayList<Process>(procs.size());
        fs = new FormatedStdout("RR", limit);
        this.t_cs = t_cs;
        this.t_slice = t_slice;
        this.add_end = add_end;
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
    public float[] simulate() {
        // print all processes
        fs.printAll(actionList);
        System.out.println("time 0ms: Simulator started for RR [Q <empty>]");
        actionList.sort(new _sortByState());
        // store process that is in load state
        Process btProc = null; // process with LOAD or BURST or UNLOAD state
        while (actionList.size() != 0) {

            // get time from next process
            clock = actionList.get(0).kTime;
            // if (clock == 467) {
            //     int X = 0;
            // }

            while (actionList.size() > 0 && actionList.get(0).kTime == clock) {
                Process proc = actionList.remove(0);
                switch (proc.state) {
                    case NEW:
                        proc.state = States.READY;
                        if (add_end) {
                            readyList.add(readyList.size(), proc);
                        } else {
                            readyList.add(0, proc);
                        }

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
                        proc.kTime += Math.min(t_slice, proc.remain);
                        // proc.csCount += 1; // context switch
                        fs.printStartedBurst(clock, proc, readyList);
                        actionList.add(proc);
                        break;

                    case BURST:
                        proc.remain -= t_slice;
                        if (proc.remain > 0 && readyList.size() == 0) {
                            // no process in ready state, keep going
                            proc.kTime += Math.min(t_slice, proc.remain);
                            fs.printSlcExp(clock, proc, readyList);
                        } else {
                            proc.state = States.UNLOAD;
                            proc.kTime += t_cs >> 1;
                            if (proc.remain > 0) {
                                // time slice expires
                                fs.printSlcExp(clock, proc, readyList);
                            } else if (proc.burstTimes.length - proc.progress == 1) {
                                // process terminated, but unload from CPU first
                                fs.printTerminate(clock, proc, readyList);
                            } else {
                                fs.printEndedBurst(clock, proc, readyList);
                                proc.kTime += proc.blockTimes[proc.progress]; // just for print
                                fs.printStartedBlock(clock, proc, readyList);
                                proc.kTime -= proc.blockTimes[proc.progress];
                            }
                        }

                        actionList.add(proc);
                        break;

                    case UNLOAD:
                        // unloaded from CPU
                        if (proc.remain > 0) {
                            proc.state = States.READY;
                            proc.pmCount += 1;
                            if (add_end) {
                                readyList.add(readyList.size(), proc);
                            } else {
                                readyList.add(0, proc);
                            }
                        } else if (proc.burstTimes.length - proc.progress == 1) {
                            // no more burst to go, process terminate
                            proc.state = States.TERMINATED;
                            endedList.add(proc);
                        } else {
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
                        if (add_end) {
                            readyList.add(readyList.size(), proc);
                        } else {
                            readyList.add(0, proc);
                        }
                        fs.printEndedBlock(clock, proc, null, readyList);
                        break;

                    default:
                        System.err.println("Error: unexpected state.");
                        System.exit(-1);
                }

                // sort
                actionList.sort(new _sortByState());
            }

            // empty CPU, add new process
            if (btProc == null && readyList.size() > 0) {
                Process tmp = readyList.remove(0);
                tmp.kTime = clock;
                actionList.add(tmp);
                actionList.sort(new _sortByState());
            }
        }

        System.out.printf("time %dms: Simulator ended for RR ", clock);
        fs.printReady(readyList);

        float retVal[] = new float[5];
        calRetVal(retVal);
        // System.err.printf("%.3f %.3f %.3f %.0f %.0f\n", retVal[0], retVal[1], retVal[2], retVal[3], retVal[4]);
        return retVal;
    }
}
