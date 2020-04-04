import enum


class Action(enum.Enum):
    new = 0         # process have not arrive at CPU
    ready = 1       # ready to use CPU
    running = 2     # actively using CPU
    blocked = 3     # I/O time
    terninated = 4  # process terninates


class Process:
    def __init__(self, name: str):
        self.name = name
        self.arrival_time = 0    # process arrival time, in MILLISECONDS

        self.burst_time = []  # CPU burst time in MS
        self.block_time = []  # I/O block time in MS
        self.burst_index = 0
        self.block_index = 0
        self.total_burst = 0  # sum(self.burst_time)
        self.total_block = 0  # sum(self.block_time)

        # process current status
        self.action = Action.new
        # time of the process finish current status in MILLISECONDS. If process
        #   enters CPU at x ms, and takes y ms CPU burst, action_exit will be
        #   x + y
        self.action_exit = 0

        self.wait_time = 0
        self.preempt_count = 0

        # use setattr(object, name, value) to add attribute with your needs


"""
Linear congruential generator, generate random numbers

Algorithm is inherited from POSIX
"""


class LCG:
    def __init__(self):
        self.seed = 0

    # initialize seed, detail implementation see man srand48
    def srand48(self, seedval: int):
        self.seed = ((seedval & 0xFFFFFFFF) << 16) | 0x330E

    # get random number, detail implementation see man drand48
    def drand48(self) -> float:
        self.seed = (0x5DEECE66D * self.seed + 0xB) & 0xffffffffffff
        return float(self.seed / 0x1000000000000)
