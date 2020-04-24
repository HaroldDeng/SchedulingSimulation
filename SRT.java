// import java.util.*;

// public class SRT {
//     private PriorityQueue<Process> arriveQueue;
//     private PriorityQueue<Process> readyQueue;
//     private List<Process> burstList;
//     private Process[] processes;

//     public SRT() {
//         this.processes = Process.generateProcesses(true);
//         this.readyQueue = new PriorityQueue<>(new Comparator<Process>() {
//             @Override
//             public int compare(Process o1, Process o2) {
//                 int time1 = o1.estimates[o1.index] - o1.burstedTime;
//                 int time2 = o2.estimates[o2.index] - o2.burstedTime;
//                 if (time1 == time2) {
//                     return o1.name.compareTo(o2.name);
//                 } else {
//                     return time1 - time2;
//                 }
//             }
//         });
//         this.burstList = new ArrayList<>();
//         this.arriveQueue = new PriorityQueue<>(new Comparator<Process>() {
//             @Override
//             public int compare(Process arg0, Process arg1) {
//                 return arg0.arriveTime - arg1.arriveTime;
//             }
//         });
//     }

//     public double[] simulate() {
//         String result = "Algorithm SRT\n";
//         System.out.println("time 0ms: Simulator started for SRT [Q <empty>]");
//         int total = 0;
//         int totalBursts = 0;
//         Process proc = Process.EMPTY;
//         int clock = 0;
//         int finished = 0;
//         int sum_cs = 0;
//         int sum_pt = 0;
//         int p_count = this.processes.length;
//         List<Process> endedList = new ArrayList<>();

//         String preemptedID = "";
//         for (Process p : this.processes) {
//             total += p.sumBurst();
//             totalBursts += p.capacity;
//         }

//         for (Process p : this.processes) {
//             if (p.remainingTime == 0) {
//                 p.setState(ProcessState.READY);
//                 this.readyQueue.add(p);
//                 System.out.printf("time %dms: Process %s (tau %dms) arrived; added to ready queue ", 0, p.name,
//                         p.estimateTime());
//                 printReady();
//             } else {
//                 this.arriveQueue.add(p);
//             }
//         }

//         while (finished != p_count) {
//             clock++;

//             if (!endedList.isEmpty()) {
//                 endedList.clear();
//             }

//             for (Process p : burstList) {
//                 boolean status = p.tick();
//                 if (status) {
//                     p.burstedTime = 0;
//                     endedList.add(p);
//                 }
//             }

//             int arriveNum = 0;
//             for (Process p : arriveQueue) {
//                 boolean changedState = p.tick();
//                 if (changedState) {
//                     p.burstedTime = 0;
//                     arriveNum++;
//                 }
//             }

//             if (proc != Process.EMPTY) {
//                 boolean changedState = proc.tick();
//                 if (changedState) {
//                         if (proc.state == ProcessState.ENTER_CPU){
//                             proc.setState(ProcessState.BURST);
//                             proc.setPreempted(false);
//                             System.out.printf(
//                                     "time %dms: Process %s (tau %dms) started using the CPU with %dms burst remaining ",
//                                     clock, proc.name, proc.estimateTime(), proc.remainingTime - proc.burstedTime);
//                             printReady();

//                             proc.changeRemainingTime();
//                             if (!readyQueue.isEmpty()
//                                     && readyQueue.peek().estimateTime() < proc.estimatedRemainingTime()) {
//                                 System.out.printf("time %dms: Process %s (tau %dms) will preempt %s ", clock,
//                                         readyQueue.peek().name, readyQueue.peek().estimateTime(), proc.name);
//                                 printReady();

//                                 sum_pt++;
//                                 proc.setPreempted(true);
//                                 proc.setState(ProcessState.LEAVE_CPU); // if finished switch in and need to perform
//                                                                        // preemption, switch out
//                                 sum_cs++;
//                             }
//                         }else if(proc.state == ProcessState.BURST){
//                             proc.setState(ProcessState.LEAVE_CPU);
//                             sum_cs++;
//                             if (proc.index == proc.capacity - 1) {
//                                 System.out.printf("time %dms: Process %s terminated ", clock, proc.name);
//                                 printReady();
//                             } else {
//                                 if (proc.capacity - proc.index - 1 != 1) {
//                                     System.out.printf(
//                                             "time %dms: Process %s (tau %dms) completed a CPU burst; %d bursts to go ",
//                                             clock, proc.name, proc.estimateTime(), proc.capacity - proc.index - 1);
//                                     printReady();

//                                 } else {
//                                     System.out.printf(
//                                             "time %dms: Process %s (tau %dms) completed a CPU burst; %d burst to go ",
//                                             clock, proc.name, proc.estimateTime(), proc.capacity - proc.index - 1);
//                                     printReady();
//                                 }

//                                 System.out.printf("time %dms: Recalculated tau = %dms for process %s ", clock,
//                                         proc.nextEstiTime(), proc.name);
//                                 printReady();
//                                 System.out.printf(
//                                         "time %dms: Process %s switching out of CPU; will block on I/O until time %dms ",
//                                         clock, proc.name, clock + Project.t_cs / 2 + proc.getIOTime());
//                                 printReady();

//                             }
//                         }else if(proc.state == ProcessState.LEAVE_CPU){
//                             if (proc.isEnded()) {
//                                 finished++;

//                                 proc.setState(ProcessState.TERMINATED);
//                                 proc.leaveCPU = clock;
//                             } else {

//                                 if (proc.preempted) {
//                                     proc.setState(ProcessState.READY);
//                                     proc.setRemainingTime();
//                                     readyQueue.add(proc);
//                                     preemptedID = proc.name;
//                                 } else {
//                                     proc.setState(ProcessState.BLOCK);
//                                     proc.burstedTime = 0;
//                                     proc.setPreempted(false);
//                                     burstList.add(proc);
//                                 }
//                             }

//                             proc = Process.EMPTY;
//                         }else{
//                             System.err.println("Error: unexpected state.");
//                             System.exit(-1);
//                         }
                    
//                 }
//             } else {
//                 if (!this.readyQueue.isEmpty()) {
//                     proc = this.readyQueue.poll();
//                     proc.setState(ProcessState.ENTER_CPU);
//                     sum_cs++;

//                     boolean changedState = proc.tick();
//                     if (changedState) {
//                         proc.setState(ProcessState.BURST);
//                         System.out.printf(
//                                 "time %dms: Process %s (tau %dms) started using the CPU with %dms burst remaining ",
//                                 clock, proc.name, proc.estimateTime(), proc.remainingTime - proc.burstedTime);
//                         printReady();

//                     }
//                 }
//             }

//             for (Process p : readyQueue) {
//                 if (!p.name.equals(preemptedID)) {
//                     p.addWaitingTime();
//                 }

//             }
//             preemptedID = "";

//             Collections.sort(endedList, new Comparator<Process>() {
//                 @Override
//                 public int compare(Process arg0, Process arg1) {
//                     return arg0.name.compareTo(arg1.name);
//                 }
//             });
//             // finished io processes
//             for (int i = 0; i < endedList.size(); i++) {
//                 Process p = endedList.get(i);
//                 p.index += 1;
//                 burstList.remove(p);
//                 readyQueue.add(p);
//                 if (i == 0 && proc != null && proc.state.equals(ProcessState.BURST)
//                         && p.estimateTime() < proc.estimatedRemainingTime()) {
//                     System.out.printf("time %dms: Process %s (tau %dms) completed I/O; preempting %s ", clock, p.name,
//                             p.estimateTime(), proc.name);
//                     printReady();

//                     proc.setState(ProcessState.LEAVE_CPU);
//                     sum_pt++;
//                     sum_cs++;
//                     proc.setPreempted(true);
//                 } else {
//                     System.out.printf("time %dms: Process %s (tau %dms) completed I/O; added to ready queue ", clock,
//                             p.name, p.estimateTime());
//                     printReady();

//                 }
//             }

//             for (int i = 0; i < arriveNum; i++) {
//                 Process p = arriveQueue.poll();
//                 p.setState(ProcessState.READY);
//                 p.burstedTime = 0;
//                 readyQueue.add(p);

//                 System.out.printf("time %dms: Process %s (tau %dms) arrived; added to ready queue ", clock, p.name,
//                         p.estimateTime());
//                 printReady();

//             }
//         }

//         System.out.println(String.format("time %dms: Simulator ended for SRT [Q <empty>]", clock));

//         double avg_bt = (double) total / (double) totalBursts;
//         int totalWaitingTime = 0;
//         for (Process p : processes) {
//             totalWaitingTime += p.getWaitingTime();
//         }
//         result += String.format("-- average wait time: %.3f ms\n", (double) totalWaitingTime / (double) totalBursts);

//         double avg_wt = (double) totalWaitingTime / (double) totalBursts;
        
//         int totalTurnaroundTime = 0;
//         for (Process p : processes) {
//             totalTurnaroundTime += (p.leaveCPU - p.arriveTime - p.getTotalIOTime());
//         }
//         double avg_tt = (double) totalTurnaroundTime / (double) totalBursts;

//         double retVal[] = new double[] { avg_bt, avg_wt, avg_tt, sum_cs / 2, sum_pt };
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
//             tmpList.add(readyQueue.poll());
//         }
//         Collections.sort(tmpList, new Comparator<Process>() {
//             @Override
//             public int compare(Process o1, Process o2) {
//                 int t1 = o1.estimates[o1.index] - o1.burstedTime;
//                 int t2 = o2.estimates[o2.index] - o2.burstedTime;
//                 if (t1 == t2) {
//                     return o1.name.compareTo(o2.name);
//                 } else {
//                     return t1 - t2;
//                 }
//             }
//         });
//         for (int i = 0; i < tmpList.size(); i++) {
//             str += String.format(" %s", tmpList.get(i).name);
//         }
//         str += "]";
//         for (int i = 0; i < tmpList.size(); i++) {
//             readyQueue.add(tmpList.get(i));
//         }

//         System.out.println(str);
//     }
// }