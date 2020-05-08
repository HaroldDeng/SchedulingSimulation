test2:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 2 0.01 256 1 4 0.5 128 > out.txt

test3:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 2 0.01 256 2 4 0.5 128 > out.txt

test4:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 2 0.01 256 16 4 0.5 128 > out.txt

test5:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 64 0.001 4096 8 4 0.5 2048 > out.txt

test6:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 2 0.01 256 2 4 0.5 128 > out.txt


clear:
	> out.txt
	rm *.class

# test for project write-up
ptest:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 0 0.01 32768 26 6 0.5 64 BEGINNING > out.txt
ptest2:
	> out.txt
	javac Project.java util.java FCFS.java RR.java SJF.java SRT.java
	java Project 0 0.01 32768 26 6 0.5 64 > out.txt