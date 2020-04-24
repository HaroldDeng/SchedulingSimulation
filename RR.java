// import java.util.ArrayList;
// import java.util.Comparator;
// import java.util.LinkedList;
// import java.util.List;
// import java.util.PriorityQueue;

// public class RR {
//     private Process[] processes;
//     private PriorityQueue<Process> arriveQueue;
//     private List<Process> readyList;
//     private List<Process> burstList;

//     public RR() {
//         this.processes = Process.generateProcesses(false);
//         this.arriveQueue = new PriorityQueue<Process>(new Comparator<Object>() {
//             @Override
//             public int compare(Object arg0, Object arg1) {
//                 return ((Process) arg0).arriveTime - ((Process) arg1).arriveTime;
//             }
//         });
//         this.readyList = new ArrayList<Process>();
//         this.burstList = new ArrayList<Process>();
//     }

//     public double[] simulate() {
//         String result = "Algorithm RR\n";
//         System.out.println("time 0ms: Simulator started for RR [Q <empty>]");

//         // initialize arriveQueue and add process with arriveTime = 0 into readyList
//         for (int i = 0; i < processes.length; i++) {

//             if (processes[i].remainingTime == 0) {
//                 processes[i].setState(ProcessState.READY);
//                 if (Project.add_end)
//                     readyList.add(processes[i]);
//                 else
//                     readyList.add(0, processes[i]);
//                 System.out.printf("time %dms: Process %s arrived; added to ready queue ", 0, processes[i].name);
//                 printReady();
//             } else {
//                 arriveQueue.add(processes[i]);
//             }
//         }

//         Process proc = Process.EMPTY;
//         int clock = 0;
//         int slice = Project.t_slice;
//         int endNum = 0;
//         int proc_count = processes.length;
//         int sum_cs = 0;
//         int sum_pt = 0;
//         LinkedList<Process> tmpList = new LinkedList<Process>();
//         Process tmp = null;

//         while (proc != Process.EMPTY || endNum != proc_count) {
//             clock++;
//             tmpList.clear();

//             // Ticking processes in ioList
//             for (Process p : burstList) {
//                 if (p.tick()) {
//                     tmpList.add(p);
//                 }
//             }

//             // Ticking processes in arriveQueue
//             int arriveNum = 0;
//             for (Process p : arriveQueue) {
//                 if (p.tick()) {
//                     arriveNum++;
//                 }
//             }

//             // Ticking process in running
//             if (proc == Process.EMPTY) {
//                 if (!readyList.isEmpty()) {
//                     proc = readyList.remove(0);
//                     proc.setState(ProcessState.ENTER_CPU);
//                     slice = Project.t_slice;
//                     if (proc.tick()) {
//                         sum_cs++;
//                         proc.setState(ProcessState.BURST);
//                         proc.setRemainingTime();
//                         System.out.printf("time %dms: Process %s started using the CPU for %dms burst ", clock,
//                                 proc.name, proc.remainingTime);
//                         printReady();
//                     }
//                 }
//             } else {
//                 if (proc.tick()) {
//                     if (proc.state == ProcessState.ENTER_CPU) {
//                         sum_cs++;
//                         proc.setState(ProcessState.BURST);
//                         proc.setRemainingTime();
//                         if (proc.preempted) {
//                             proc.setPreempted(false);
//                             System.out.printf("time %dms: Process %s started using the CPU with %dms burst remaining ",
//                                     clock, proc.name, proc.remainingTime);
//                             printReady();
//                         } else {
//                             System.out.printf("time %dms: Process %s started using the CPU for %dms burst ", clock,
//                                     proc.name, proc.remainingTime);
//                             printReady();
//                         }
//                     } else if (proc.state == ProcessState.LEAVE_CPU) {
//                         sum_cs++;
//                         if (proc.preempted) {
//                             tmp = proc;
//                             proc.setState(ProcessState.READY);
//                             if (Project.add_end)
//                                 readyList.add(proc);
//                             else
//                                 readyList.add(0, proc);
//                         } else if (proc.index == proc.capacity - 1) {
//                             endNum++;
//                             proc.leaveCPU = clock;
//                             proc.burstedTime = 0;
//                             proc.setState(ProcessState.TERMINATED);
//                         } else {
//                             proc.setState(ProcessState.BLOCK);
//                             proc.burstedTime = 0;
//                             burstList.add(proc);
//                         }
//                         proc = Process.EMPTY;
//                     } else if (proc.state == ProcessState.BURST) {
//                         proc.setState(ProcessState.LEAVE_CPU);
//                         if (proc.index == proc.capacity - 1) {
//                             System.out.printf("time %dms: Process %s terminated ", clock, proc.name);
//                             printReady();
//                         } else {
//                             if (proc.capacity - proc.index == 2) {
//                                 System.out.printf("time %dms: Process %s completed a CPU burst; %d burst to go ", clock,
//                                         proc.name, proc.capacity - proc.index - 1);
//                             } else {
//                                 System.out.printf("time %dms: Process %s completed a CPU burst; %d bursts to go ",
//                                         clock, proc.name, proc.capacity - proc.index - 1);
//                             }
//                             printReady();

//                             System.out.printf(
//                                     "time %dms: Process %s switching out of CPU; will block on I/O until time %dms ",
//                                     clock, proc.name, clock + Project.t_cs / 2 + proc.getIOTime());
//                             printReady();
//                         }
//                     } else {
//                         System.err.println("Error: unexpected state.");
//                         System.exit(-1);
//                     }
//                 } else {
//                     if (proc.state == ProcessState.BURST) {
//                         slice--;
//                         if (slice == 0) {
//                             if (readyList.isEmpty()) {
//                                 System.out.printf(
//                                         "time %dms: Time slice expired; no preemption because ready queue is empty ",
//                                         clock);
//                                 printReady();
//                             } else {
//                                 System.out.printf(
//                                         "time %dms: Time slice expired; process %s preempted with %dms to go ", clock,
//                                         proc.name, proc.remainingTime);
//                                 printReady();
//                                 sum_pt++;
//                                 proc.setPreempted(true);
//                                 proc.setState(ProcessState.LEAVE_CPU);
//                             }
//                             slice = Project.t_slice;
//                         }
//                     }
//                 }
//             }

//             for (Process p : readyList) {
//                 if (p == tmp) {
//                     continue;
//                 }

//                 p.addWaitingTime();
//             }
//             tmp = null;

//             // Add from IO to READY
//             if (!tmpList.isEmpty()) {
//                 tmpList.sort(new Comparator<Object>() {
//                     @Override
//                     public int compare(Object arg0, Object arg1) {
//                         return ((Process) arg0).name.compareTo(((Process) arg1).name);
//                     }
//                 });
//                 for (Process p : tmpList) {
//                     p.index += 1;
//                     burstList.remove(p);
//                     if (Project.add_end)
//                         readyList.add(p);
//                     else
//                         readyList.add(0, p);
//                     System.out.printf("time %dms: Process %s completed I/O; added to ready queue ", clock, p.name);
//                     printReady();
//                 }
//             }

//             // Add from ARRIVE to READY
//             for (int i = 0; i < arriveNum; i++) {
//                 Process p = arriveQueue.remove();
//                 if (Project.add_end)
//                     readyList.add(p);
//                 else
//                     readyList.add(0, p);
//                 System.out.printf("time %dms: Process %s arrived; added to ready queue ", clock, p.name);
//                 printReady();
//             }

//         }

//         System.out.print(String.format("time %dms: Simulator ended for RR ", clock));
//         printReady();
//         int burstNum = 0;
//         for (Process p : processes) {
//             burstNum += p.capacity;
//         }

//         sum_cs /= 2;

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
//                         + "-- total number of preemptions: %d\n",
//                 avg_bt, avg_wt, avg_tt, sum_cs, sum_pt);
//         double retVal[] = new double[] { avg_bt, avg_wt, avg_tt, sum_cs / 2, sum_pt };

//         return retVal;
//     }

//     private void printReady() {
//         if (readyList.size() == 0) {
//             System.out.println("[Q <empty>]");
//             return;
//         }

//         String str = "[Q";
//         for (Process p : readyList) {
//             str += String.format(" %s", p.name);
//         }
//         System.out.println(str + "]");
//     }

//     private String queueInfo() {
//         if (readyList.isEmpty()) {
//             return "[Q <empty>]";
//         }

//         String str = "[Q";
//         for (Process p : readyList) {
//             str += String.format(" %s", p.name);
//         }
//         str += "]";
//         return str;
//     }

// }