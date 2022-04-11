import pickle
import threading

from model import Container, JudgeTask
from service.generate_tasks.generate import TaskGenerator


class Scheduler:
    def __init__(self, containers: list[Container]):
        self.containers = containers

    def deliver_task(self, task):
        # iterate containers weight
        min_weight = -1
        selected = -1
        for idx, container in enumerate(self.containers):
            current_weight = container.status()
            if min_weight == -1 or min_weight > current_weight:
                min_weight = current_weight
                selected = idx

        self.containers[selected].add_tasks([task])

    def deliver_tasks(self, tasks):
        for task in tasks:
            self.deliver_task(task)

    def start(self, path: str = ""):
        threading_pool = [
            threading.Thread(target=container.run_tasks) for container in self.containers
        ]
        # get tasks
        tasks: list[JudgeTask] = []
        if path != "":
            with open(path, "rb") as f:
                tasks = pickle.load(f)
        else:
            g = TaskGenerator()
            tasks = g.generate_n_tasks(10, 100)
        self.deliver_tasks(tasks)
        for thr in threading_pool:
            thr.start()
