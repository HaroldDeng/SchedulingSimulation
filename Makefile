test2:
	> out.txt
	javac project1.java util.java FCFS.java RR.java SJF.java SRT.java
	java project1 2 0.01 256 1 4 0.5 128 > out.txt

test3:
	> out.txt
	javac project1.java util.java FCFS.java RR.java SJF.java SRT.java
	java project1 2 0.01 256 2 4 0.5 128 > out.txt

test4:
	> out.txt
	javac project1.java util.java FCFS.java RR.java SJF.java SRT.java
	java project1 2 0.01 256 16 4 0.5 128 > out.txt

test5:
	> out.txt
	javac project1.java util.java FCFS.java RR.java SJF.java SRT.java
	java project1 64 0.001 4096 8 4 0.5 2048 > out.txt

test6:
	> out.txt
	javac project1.java util.java FCFS.java RR.java SJF.java SRT.java
	java project1 64 0.001 4096 8 4 0.5 2048 BEGINNING > out.txt


clear:
	> out.txt
	rm *.class