import java.util.List;

public class ScheAlgo {
    List<Process> readyList; // processes in ready state
    List<Process> actionList; // CPU busrting or I/O blocking
    List<Process> endedList; // processes that is terminated
    FormatedStdout fs;
    int t_cs;
    int clock;
    boolean add_end;

    double[] simulate() {
        return null;
    };

    void calRetVal(double[] retVal) {
        int count = 0;
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
            retVal[1] += (proc.kTime - proc.arriveTime - sum_burst - sum_block - proc.csCount * t_cs)
                    / (double) proc.burstTimes.length;
            retVal[2] += (sum_burst + proc.csCount * t_cs) / (double) proc.burstTimes.length;
            retVal[3] += proc.csCount;
            retVal[4] += proc.pmCount;
        }
        retVal[0] /= count;
        retVal[1] /= endedList.size();
        retVal[2] /= endedList.size();

    }

}