import threading

from exception import CreateContainerError
from model import JudgeTask


class Container:
    def __init__(self, config: dict):
        self.available = True
        self.task_queue: list[JudgeTask] = []
        self.container_id = config.get("container_id")
        self.memory = config.get("memory")
        self.machine_id = config.get("machine_id")
        self.history = []
        self.task_count = 0
        self.lock = threading.Lock()
        self.weight = 0  # estimated time
        self.time_line = 0
        self.statistic = {
            "finished": 0,
            "time_cost": 0,
        }

    def status(self):
        self.lock.acquire()
        weight = self.weight
        self.lock.release()
        return weight

    def add_tasks(self, tasks: list[JudgeTask]):
        self.lock.acquire()
        self.task_queue.extend(tasks)
        for task in tasks:
            self.weight += task.problem_info.tle_rate * task.limited_time
        self.lock.release()

    def get_task(self):
        self.lock.acquire()
        try:
            task = self.task_queue.pop(0)
        except IndexError:
            self.lock.release()
            return None

        self.lock.release()
        return task

    def run_tasks(self):
        task = self.get_task()
        while task:
            self.statistic["time_cost"] += task.exec_time
            self.statistic["finished"] += 1
            task = self.get_task()
        print(self.statistic)
