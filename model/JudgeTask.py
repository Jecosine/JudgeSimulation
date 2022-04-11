from typing import *


class ProblemInfo:
    def __init__(self, problem_id: int, tle_rate: float, mle_rate: float, limited_time: int,
                 limited_memory: int):
        self.mle_rate = mle_rate
        self.tle_rate = tle_rate
        self.problem_id = problem_id
        self.limited_time = limited_time
        self.limited_memory = limited_memory


class JudgeTask:
    def __init__(self, tid: int, problem_info: ProblemInfo, code: str, limited_time: int,
                 limited_memory: int, exec_time: float, exec_memory: int):
        """
        Args:
            tid:
            problem_info:
            code:
            limited_time:
            limited_memory:
        """
        self.code = code
        self.limited_time = limited_time
        self.limited_memory = limited_memory
        self.problem_info = problem_info
        self.tid = tid

        self.exec_time = exec_time
        self.exec_memory = exec_memory

    def info(self):
        return {
            'tid': self.tid,
            'limited_time': self.limited_time,
            'limited_memory': self.limited_memory,
        }
