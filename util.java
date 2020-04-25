import java.util.Comparator;
import java.util.List;

enum States {
    NEW, READY, LOAD, BURST, UNLOAD, BLOCK, TERMINATED
}

class Process implements Cloneable {
    public char name;
    public int arriveTime;

    int[] burstTimes; // do not modify, uses to cal. tau
    int[] blockTimes;
    int progress;
    int remain; // burst remain

    States state;
    int kTime; // key clock, clock to next state

    int tau;
    int pmCount; // preemption count
    int csCount; // context switch count

    Process(char name) {
        this.name = name;
    }

    // clone this object
    @Override
    public Process clone() throws CloneNotSupportedException {
        return (Process) super.clone();
    }

    public boolean tick() {
        kTime--;

        if (state == States.BURST) {
            kTime++;
        } else if (state == States.READY) {
            kTime++;
        }

        return kTime == 0;
    }

}

class FormatedStdout {

    // if clock is greater than this value, and is not
    // termination string, string will not be output
    private int limit;

    // schedualing mode
    private String mode;

    public FormatedStdout(String mode, int limit) {
        this.mode = mode;
        this.limit = limit;
    }

    public void printAll(List<Process> readyList) {
        if (mode.matches("FCFS|RR")) {
            for (Process p : readyList) {
                if (p.burstTimes.length > 1) {
                    System.out.printf("Process %c [NEW] (arrival time %d ms) %d CPU bursts\n", p.name, p.arriveTime,
                            p.burstTimes.length);
                } else {
                    System.out.printf("Process %c [NEW] (arrival time %d ms) 1 CPU burst\n", p.name, p.arriveTime);

                }

            }
        } else {
            for (Process p : readyList) {
                if (p.burstTimes.length > 1) {
                    System.out.printf("Process %c [NEW] (arrival time %d ms) %d CPU bursts (tau %dms)\n", p.name,
                            p.arriveTime, p.burstTimes.length, p.tau);
                } else {
                    System.out.printf("Process %c [NEW] (arrival time %d ms) 1 CPU burst (tau %dms)\n", p.name,
                            p.arriveTime, p.tau);
                }

            }
        }

    }

    public void printArrival(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        } else if (mode.matches("FCFS|RR")) {
            // time 9ms: Process A arrived; added to ready queue [Q A]
            System.out.printf("time %dms: Process %c arrived; added to ready queue ", clock, proc.name);
        } else {
            System.out.printf("time %dms: Process %c (tau %dms) arrived; added to ready queue ", clock, proc.name,
                    proc.tau);
        }
        printReady(readyList);
    }

    public void printStartedBurst(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        } else if (mode.compareTo("FCFS") == 0) {
            System.out.printf("time %dms: Process %c started using the CPU for %dms burst ", clock, proc.name,
                    proc.remain);
        } else {
            // proc.remain != proc.burstTimes[proc.progress]
            System.out.printf("time %dms: Process %c ", clock, proc.name);
            if (mode.matches("SRT|SJF")) {
                // started using the CPU with %dms burst remaining
                System.out.printf("(tau %dms) ", proc.tau);
            }

            if (mode.compareTo("SRT") == 0
                    || (mode.compareTo("RR") == 0 && proc.remain != proc.burstTimes[proc.progress])) {
                System.out.printf("started using the CPU with %dms burst remaining ", proc.remain);
            } else {
                System.out.printf("started using the CPU for %dms burst ", proc.remain);
            }
        }
        printReady(readyList);
    }

    public void printEndedBurst(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        } else if (mode.matches("FCFS|RR")) {
            System.out.printf("time %dms: Process %c completed a CPU burst; ", clock, proc.name);
        } else {
            System.out.printf("time %dms: Process %c (tau %dms) completed a CPU burst; ", clock, proc.name, proc.tau);
        }

        if (proc.burstTimes.length - proc.progress == 2) {
            System.out.printf("1 burst to go ");
        } else {
            System.out.printf("%d bursts to go ", proc.burstTimes.length - proc.progress - 1);
        }
        printReady(readyList);
    }

    public void printReTau(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        }
        System.out.printf("time %dms: Recalculated tau = %dms for process %c ", clock, proc.tau, proc.name);
        printReady(readyList);
    }

    // !!! emergency fix
    // for SRT only
    public void printCutPree(int clock, Process proc, Process proc2, List<Process> readyList) {
        if (clock > limit) {
            return;
        }
        System.out.printf("time %dms: Process %c (tau %dms) will preempt %c ", clock, proc.name, proc.tau, proc2.name);
        printReady(readyList);
    }

    // !!! emergency fix
    // for RR only
    public void printSlcExp(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        } else if (readyList.size() > 0) {
            System.out.printf("time %dms: Time slice expired; process %c preempted with %dms to go ", clock, proc.name,
                    proc.remain);
        } else {
            System.out.printf("time %dms: Time slice expired; no preemption because ready queue is empty ", clock);
        }

        printReady(readyList);
    }

    public void printStartedBlock(int clock, Process proc, List<Process> readyList) {
        if (clock > limit) {
            return;
        }
        System.out.printf("time %dms: Process %c switching out of CPU; will block on I/O until time %dms ", clock,
                proc.name, proc.kTime);
        printReady(readyList);
    }

    public void printEndedBlock(int clock, Process proc, Process proc2, List<Process> readyList) {
        if (clock > limit) {
            return;
        } else if (mode.matches("FCFS|RR")) {
            // no preemption
            System.out.printf("time %dms: Process %c completed I/O; added to ready queue ", clock, proc.name);
        } else if (proc2 != null) {
            // preemption
            System.out.printf("time %dms: Process %c (tau %dms) completed I/O; preempting %c ", clock, proc.name,
                    proc.tau, proc2.name);
        } else {
            System.out.printf("time %dms: Process %c (tau %dms) completed I/O; added to ready queue ", clock, proc.name,
                    proc.tau);
        }
        printReady(readyList);
    }

    public void printTerminate(int clock, Process proc, List<Process> readyList) {
        // print termination string is a must, no need to check clock
        System.out.printf("time %dms: Process %c terminated ", clock, proc.name);
        printReady(readyList);
    }

    public void printReady(List<Process> readyList) {
        System.out.print("[Q");
        if (readyList.size() == 0) {
            System.out.print(" <empty>");
        } else {
            for (Process p : readyList) {
                System.out.print(String.format(" %c", p.name));
            }
        }

        System.out.println("]");
    }
}

class _sortByEstmate implements Comparator<Process> {
    @Override
    public int compare(Process p1, Process p2) {
        int est1 = p1.tau - p1.burstTimes[p1.progress] + p1.remain;
        int est2 = p2.tau - p2.burstTimes[p2.progress] + p2.remain;
        if (est1 != est2) {
            return est1 - est2;
        }
        return p1.name - p2.name;
    }
}

class _sortByState implements Comparator<Process> {
    @Override
    public int compare(Process p1, Process p2) {
        if (p1.kTime != p2.kTime) {
            return p1.kTime - p2.kTime;
        } else if (p1.state == States.READY && p2.state != States.READY) {
            // p1 is ready for load into CPU
            return -1;
        } else if (p1.state == States.LOAD && p2.state != States.LOAD) {
            // p1 is loaded into CPU
            if (p2.state == States.READY) {
                return 1;
            }
            return -1;
        } else if (p1.state == States.BURST && p2.state != States.BURST) {
            // p1 is CPU burst complete
            if (p2.state == States.READY || p2.state == States.LOAD) {
                return 1;
            }
            return -1;
        } else if (p1.state == States.UNLOAD && p2.state != States.UNLOAD) {
            // p1 is unloaded from CPU
            if (p2.state == States.BLOCK || p2.state == States.NEW) {
                return -1;
            }
            return 1;
        } else if (p1.state == States.BLOCK && p2.state != States.BLOCK) {
            // p1 is block complete
            if (p2.state == States.NEW) {
                return -1;
            }
            return 1;
        } else if (p1.state == States.NEW && p2.state != States.NEW) {
            // p1 is newly arrive process
            return 1;
        }
        return p1.name - p2.name;

        // ignore terminated state
    }
}

/**
 * Linear congruential generator, generate random numbers. Algorithm is
 * inherited from POSIX
 */
class LCG48 {
    private long seed;

    public void srand48(long seed) {
        this.seed = ((seed & 0xFFFFFFFFL) << 16) | 0x330EL;
    }

    public double drand48() {
        this.seed = (0x5DEECE66DL * this.seed + 0xB) & 0xffffffffffffL;
        return (double) this.seed / 0x1000000000000L;
    }
}
