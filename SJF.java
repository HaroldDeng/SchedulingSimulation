// import java.util.*;

// public class SJF {
//     private Process[] processes;
//     private PriorityQueue<Process> arriveQueue;
//     private PriorityQueue<Process> readyQueue;
//     private LinkedList<Process> ioList;

//     public SJF() {
//         this.processes = Process.generateProcesses(true);
//         this.arriveQueue = new PriorityQueue<Process>(new Comparator<Process>() {
//             @Override
//             public int compare(Process arg0, Process arg1) {
//                 return arg0.arriveTime - arg1.arriveTime;
//             }
//         });
//         this.readyQueue = new PriorityQueue<Process>(new Comparator<Process>() {

//             @Override
//             public int compare(Process p1, Process p2) {
//                 int e1 = p1.estimates[p1.index];
//                 int e2 = p2.estimates[p2.index];
//                 if (e1 == e2)
//                     return p1.name.compareTo(p2.name);
//                 else
//                     return p1.estimates[p1.index] - p2.estimates[p2.index];
//             }
//         });
//         this.ioList = new LinkedList<Process>();
//     }

//     public double[] simulate() {
//         String result = "Algorithm SJF\n";
//         System.out.println("time 0ms: Simulator started for SJF [Q <empty>]");

//         // initialize arriveQueue and add process with arriveTime = 0 into readyList
//         for (int i = 0; i < processes.length; i++) {

//             if (processes[i].remainingTime == 0) {
//                 processes[i].setState(ProcessState.READY);
//                 readyQueue.add(processes[i]);
//                 System.out.printf("time %dms: Process %s (tau %dms) arrived; added to ready queue ", 0,
//                         processes[i].name, processes[i].estimates[processes[i].index]);
//                 printReady();
//             } else {
//                 arriveQueue.add(processes[i]);
//             }
//         }

//         Process proc = Process.EMPTY;
//         int time = 0;
//         int endNum = 0;
//         int processNum = processes.length;
//         LinkedList<Process> temp = new LinkedList<Process>();

//         while (proc != Process.EMPTY || endNum != processNum) {
//             time++;
//             temp.clear();

//             // Ticking processes in ioList
//             for (Process p : ioList) {
//                 if (p.tick()) {
//                     temp.add(p);
//                 }
//             }

//             // Ticking processes in arriveQueue
//             int arriveNum = 0;
//             for (Process p : arriveQueue) {
//                 if (p.tick()) {
//                     arriveNum++;
//                 }
//             }

//             // Ticking processes in running
//             if (proc != Process.EMPTY) {
//                 if (proc.tick()) {

//                     if (proc.state == ProcessState.ENTER_CPU){
//                         proc.setState(ProcessState.BURST);
//                         System.out.printf("time %dms: Process %s (tau %dms) started using the CPU for %dms burst ",
//                                 time, proc.name, proc.estimates[proc.index], proc.remainingTime);
//                         printReady();
//                     }else if(proc.state == ProcessState.BURST){
//                         proc.setState(ProcessState.LEAVE_CPU);
//                         if (proc.index == proc.capacity - 1) {
//                             System.out.printf("time %dms: Process %s terminated ", time, proc.name);
//                             printReady();
//                         } else {
//                             if (proc.capacity - proc.index == 2) {
//                                 System.out.printf(
//                                         "time %dms: Process %s (tau %dms) completed a CPU burst; 1 burst to go ", time,
//                                         proc.name, proc.estimates[proc.index]);
//                                 printReady();
//                             } else {
//                                 System.out.printf(
//                                         "time %dms: Process %s (tau %dms) completed a CPU burst; %d bursts to go ",
//                                         time, proc.name, proc.estimates[proc.index], proc.capacity - proc.index - 1);
//                                 printReady();
//                             }

//                             System.out.printf("time %dms: Recalculated tau = %dms for process %s ", time,
//                                     proc.estimates[proc.index + 1], proc.name);
//                             printReady();
//                             System.out.printf(
//                                     "time %dms: Process %s switching out of CPU; will block on I/O until time %dms ",
//                                     time, proc.name, time + Project.t_cs / 2 + proc.getIOTime());
//                             printReady();
//                         }
//                     }else if(proc.state == ProcessState.LEAVE_CPU){
//                         if (proc.index == proc.capacity - 1) {
//                             endNum++;
//                             proc.leaveCPU = time;
//                             proc.setState(ProcessState.TERMINATED);
//                         } else {
//                             proc.setState(ProcessState.BLOCK);
//                             ioList.add(proc);
//                         }

//                         proc = Process.EMPTY;
//                     }else{
//                         System.err.println("Error: unexpected state.");
//                         System.exit(-1);
//                     }
//                 }
//             } else {
//                 if (!readyQueue.isEmpty()) {
//                     proc = readyQueue.poll();
//                     proc.setState(ProcessState.ENTER_CPU);
//                     if (proc.tick()) {
//                         proc.setState(ProcessState.BURST);
//                         System.out.printf("time %dms: Process %s (tau %dms) started using the CPU for %dms burst ",
//                                 time, proc.name, proc.estimates[proc.index], proc.remainingTime);
//                         printReady();
//                     }
//                 }
//             }

//             for (Process p : readyQueue) {
//                 p.addWaitingTime();
//             }
//             // Add from IO to READY
//             if (!temp.isEmpty()) {
//                 temp.sort(new Comparator<Object>() {
//                     @Override
//                     public int compare(Object arg0, Object arg1) {
//                         return ((Process) arg0).name.compareTo(((Process) arg1).name);
//                     }
//                 });
//                 for (Process p : temp) {
//                     p.index += 1;
//                     ioList.remove(p);
//                     readyQueue.add(p);
//                     System.out.printf("time %dms: Process %s (tau %dms) completed I/O; added to ready queue ", time,
//                             p.name, p.estimates[p.index]);
//                     printReady();
//                 }
//             }
//             for (int i = 0; i < arriveNum; i++) {
//                 Process p = arriveQueue.remove();
//                 readyQueue.add(p);
//                 System.out.printf("time %dms: Process %s (tau %dms) arrived; added to ready queue ", time, p.name,
//                         p.estimates[p.index]);
//                 printReady();
//             }
//         }

//         System.out.printf("time %dms: Simulator ended for SJF ", time);
//         printReady();

//         int burstNum = 0;
//         for (Process p : processes) {
//             burstNum += p.capacity;
//         }
//         int sum_cs = burstNum;

//         double avg_bt = 0;
//         for (Process p : processes) {
//             avg_bt += p.sumBurst();
//         }
//         avg_bt = avg_bt / burstNum;

//         double avg_wt = 0;
//         for (Process p : processes) {
//             avg_wt += p.getWaitingTime();
//         }
//         avg_wt /= burstNum;

//         double avg_tt = 0;
//         for (Process p : processes) {
//             avg_tt += p.leaveCPU - p.arriveTime - p.getTotalIOTime();
//         }
//         avg_tt /= burstNum;

//         result += String.format(
//                 "-- average CPU burst time: %.3f ms\n" + "-- average wait time: %.3f ms\n"
//                         + "-- average turnaround time: %.3f ms\n" + "-- total number of context switches: %d\n"
//                         + "-- total number of preemptions: 0\n",
//                 avg_bt, avg_wt, avg_tt, sum_cs);
//         double retVal[] = new double[] { avg_bt, avg_wt, avg_tt, sum_cs, 0.0 };
//         return retVal;
//     }

//     private void printReady() {
//         if (this.readyQueue.isEmpty()) {
//             System.out.println("[Q <empty>]");
//             return;
//         }

//         String str = "[Q";

//         List<Process> tmpList = new LinkedList<>();
//         while (readyQueue.peek() != null) {
//             Process p = readyQueue.poll();
//             str += " " + p.name;
//             tmpList.add(p);
//         }

//         readyQueue.addAll(tmpList);
//         System.out.println(str + "]");
//     }


// }