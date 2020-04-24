import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * A class that represents the First Come First Serve CPU scheduling algorithm
 */
public class FCFS extends ScheAlgo{
    public FCFS(List<Process> procs, int t_cs, boolean add_end) {
        readyList = new ArrayList<Process>(procs.size());
        actionList = new ArrayList<Process>(procs.size());
        endedList = new ArrayList<Process>(procs.size());
        fs = new FormatedStdout("FCFS", Integer.MAX_VALUE);
        this.t_cs = t_cs;
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
    public double[] simulate() {
        // print all processes
        fs.printAll(actionList);
        System.out.println("time 0ms: Simulator started for FCFS [Q <empty>]");
        actionList.sort(new _sortByState());
        // store process that is in load state
        Process btProc = null; // process with LOAD or BURST or UNLOAD state
        while (actionList.size() != 0) {
            
            // get time from next process
            clock = actionList.get(0).kTime;

            while (actionList.size() > 0 && actionList.get(0).kTime == clock) {
                Process proc = actionList.remove(0);
                switch (proc.state) {
                    case NEW:
                        proc.state = States.READY;
                        if (add_end){
                            readyList.add(readyList.size(), proc);
                        }else{
                            readyList.add(proc);
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
                        proc.kTime += proc.remain;
                        // proc.csCount += 1; // context switch
                        fs.printStartedBurst(clock, proc, readyList);
                        actionList.add(proc);
                        break;

                    case BURST:
                        // burst complete, into unload state
                        proc.state = States.UNLOAD;
                        proc.kTime += t_cs >> 1;
                        if (proc.burstTimes.length - proc.progress == 1) {
                            // process terminated, but unload from CPU first
                            fs.printTerminate(clock, proc, readyList);
                        } else {
                            fs.printEndedBurst(clock, proc, readyList);
                            proc.kTime += proc.blockTimes[proc.progress]; // just for print
                            fs.printStartedBlock(clock, proc, readyList);
                            proc.kTime -= proc.blockTimes[proc.progress];
                        }
                        actionList.add(proc);
                        break;

                    case UNLOAD:
                        // unloaded from CPU
                        if (proc.burstTimes.length - proc.progress == 1) {
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
                        if (add_end){
                            readyList.add(readyList.size(), proc);
                        }else{
                            readyList.add(proc);
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

        System.out.printf("time %dms: Simulator ended for FCFS ", clock);
        fs.printReady(readyList);

        double retVal[] = new double[5];
        // calRetVal(retVal);
        // System.err.printf("%.3f %.3f %.3f %.0f %.0f", retVal[0], retVal[1], retVal[2], retVal[3], retVal[4]);
        return retVal;
    }
}
