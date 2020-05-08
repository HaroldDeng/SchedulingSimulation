import java.util.Comparator;
import java.util.List;

public class CPUSchedual {
    List<Process> readyList; // processes in ready state
    List<Process> actionList; // CPU busrting or I/O blocking
    List<Process> endedList; // processes that is terminated
    FormatedStdout fs;
    int t_cs;
    double alpha;
    int clock;

    float[] simulate() {
        return null;
    };

    void calRetVal(float[] retVal) {
        int count = 0; // total burst count
        for (int i = 0; i < endedList.size(); ++i) {
            Process proc = endedList.get(i);
            int sum_burst = 0;
            int sum_block = 0;
            for (int br : proc.burstTimes) {
                sum_burst += br;
            }
            for (int bo : proc.blockTimes) {
                sum_block += bo;
            }
            count += proc.burstTimes.length;
            retVal[0] += sum_burst;
            retVal[1] += proc.kTime - proc.arriveTime - sum_burst - sum_block - proc.csCount * t_cs;
            retVal[2] += sum_burst + proc.csCount * t_cs;
            retVal[3] += proc.csCount;
            retVal[4] += proc.pmCount;
        }
        retVal[0] /= count;
        retVal[2] = (retVal[1] + retVal[2]) / count;
        retVal[1] /= count;

        endedList.sort(new Comparator<Process>() {
            @Override
            public int compare(Process p1, Process p2) {
                return p1.name - p2.name;
            }
        });

        // int total = 0;
        // for (Process p: endedList){
        //     total += p.kTime - p.arriveTime;
        //     // System.err.printf("%c: %d\n", p.name, p.kTime - p.arriveTime);
        // }
        // System.err.printf("%.3f\n", total / (double)endedList.size());
    }

}