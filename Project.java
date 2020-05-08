/*
    This the spring 2020 CSCI-4210's project 1, project topic is CUP scheduling
        simulation. Scheduling algorithm include first come first served, 
        shortest job first, shortest remaining time, and round robin. 
    The initial focus will be on processes, assumed to be resident in memory, 
        waiting to use the CPU. Memory and the I/O subsystem will not be covered 
        in depth in this project.
        
    Author
        Letian Zhou (zhoul10@rpi.edu)
        Zhihao Deng (dengz5@rpi.edu)

    Last modifly
        Apr.26 2020
*/

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import java.io.*;

public class Project {
    public static long seed; // pseudo-random generator's seed
    public static double lambda; // it uses in exponential distribution
    public static int bound; // upper bound for valid pseudo-random numbers
    public static int procsCount; // process count
    public static int t_cs; // context switch time in ms
    public static double alpha; // alpha for exponential averaging
    public static int t_slice; // time slice in ms
    // define whether processes are added to the end or the beginning of the ready
    // queue
    public static boolean add_end;
    public final static int LIMIT = 999;

    public static void main(String[] args) {

        // make sure # of argument is correct, 8 is optional
        if (args.length < 7 || args.length > 8) {
            System.err.println("ERROR: Invalid number of command line arguments");
            return;
        }

        try {
            seed = Long.parseLong(args[0]);
            lambda = Double.parseDouble(args[1]);
            bound = Integer.parseInt(args[2]);
            procsCount = Integer.parseInt(args[3]);
            t_cs = Integer.parseInt(args[4]);
            alpha = Double.parseDouble(args[5]);
            t_slice = Integer.parseInt(args[6]);
            if (args.length == 8 && "BEGINNING".equals(args[7])) {
                add_end = false;
            } else {
                add_end = true; // end
            }
        } catch (NumberFormatException e) {
            // error, exit
            System.err.print("ERROR: Invalid argument");
            System.exit(-1);
        }

        // generate processes
        List<Process> procs = new ArrayList<Process>(procsCount);
        initProcs(procs);

        // run algorithms
        FCFS fcfs = new FCFS(procs, t_cs, LIMIT);
        float fcfsRet[] = fcfs.simulate();
        System.out.println();

        SJF sjf = new SJF(procs, t_cs, alpha, LIMIT);
        float sjfRet[] = sjf.simulate();
        System.out.println();

        SRT srt = new SRT(procs, t_cs, alpha, LIMIT);
        float srtRet[] = srt.simulate();
        System.out.println();

        RR rr = new RR(procs, t_cs, t_slice, add_end, LIMIT);
        float rrRet[] = rr.simulate();

        // output to file
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter("simout.txt"));

            writer.write("Algorithm FCFS\n");
            writer.write(String.format("-- average CPU burst time: %.3f ms\n", fcfsRet[0]));
            writer.write(String.format("-- average wait time: %.3f ms\n", fcfsRet[1]));
            writer.write(String.format("-- average turnaround time: %.3f ms\n", fcfsRet[2]));
            writer.write(String.format("-- total number of context switches: %.0f\n", fcfsRet[3]));
            writer.write(String.format("-- total number of preemptions: %.0f\n", fcfsRet[4]));

            writer.write("Algorithm SJF\n");
            writer.write(String.format("-- average CPU burst time: %.3f ms\n", sjfRet[0]));
            writer.write(String.format("-- average wait time: %.3f ms\n", sjfRet[1]));
            writer.write(String.format("-- average turnaround time: %.3f ms\n", sjfRet[2]));
            writer.write(String.format("-- total number of context switches: %.0f\n", sjfRet[3]));
            writer.write(String.format("-- total number of preemptions: %.0f\n", sjfRet[4]));

            writer.write("Algorithm SRT\n");
            writer.write(String.format("-- average CPU burst time: %.3f ms\n", srtRet[0]));
            writer.write(String.format("-- average wait time: %.3f ms\n", srtRet[1]));
            writer.write(String.format("-- average turnaround time: %.3f ms\n", srtRet[2]));
            writer.write(String.format("-- total number of context switches: %.0f\n", srtRet[3]));
            writer.write(String.format("-- total number of preemptions: %.0f\n", srtRet[4]));

            writer.write("Algorithm RR\n");
            writer.write(String.format("-- average CPU burst time: %.3f ms\n", rrRet[0]));
            writer.write(String.format("-- average wait time: %.3f ms\n", rrRet[1]));
            writer.write(String.format("-- average turnaround time: %.3f ms\n", rrRet[2]));
            writer.write(String.format("-- total number of context switches: %.0f\n", rrRet[3]));
            writer.write(String.format("-- total number of preemptions: %.0f\n", rrRet[4]));
            writer.close();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void initProcs(List<Process> procsList) {

        // local function
        Function<LCG48, Double> boundedRNG = rng -> {
            double retVal = Math.ceil(-Math.log(rng.drand48()) / lambda);
            while (retVal > bound) {
                retVal = Math.ceil(-Math.log(rng.drand48()) / lambda);
            }
            return retVal;
        };

        // random number generator
        LCG48 rng = new LCG48();
        rng.srand48(seed);

        for (int i = 0; i < procsCount; ++i) {
            Process p = new Process((char) (65 + i));
            // p.arriveTime don't apply ceil()
            p.arriveTime = (int) (-Math.log(rng.drand48()) / lambda);
            while (p.arriveTime > bound) {
                p.arriveTime = (int) (-Math.log(rng.drand48()) / lambda);
            }
            p.burstTimes = new int[(int) (rng.drand48() * 100 + 1)];
            p.blockTimes = new int[p.burstTimes.length - 1];

            int j;
            for (j = 0; j < p.blockTimes.length; ++j) {
                p.burstTimes[j] = ((int) boundedRNG.apply(rng).doubleValue());
                p.blockTimes[j] = ((int) boundedRNG.apply(rng).doubleValue());
            }
            p.burstTimes[j] = ((int) boundedRNG.apply(rng).doubleValue());

            p.kTime = p.arriveTime;
            p.remain = p.burstTimes[0];
            p.state = States.NEW;
            p.tau = (int) (1 / lambda);
            procsList.add(p);
        }
    }

}