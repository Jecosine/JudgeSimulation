import os
import pickle
import uuid
from model import JudgeTask, ProblemInfo, Container
import numpy as np


class TaskGenerator:
    def __init__(self):
        self.task_list = []

    def clear_tasks(self):
        self.task_list.clear()

    def generate_n_tasks(self, problem_count: int, n: int, config: dict = None):
        problems = [ProblemInfo(
            problem_id=i,
            tle_rate=float(np.random.rand()),
            mle_rate=0.5,
            limited_memory=1000 * 1000,
            limited_time=200
        ) for i in range(problem_count)]
        return self.generate_n_tasks_with_problem(problems, n, config)

    def generate_n_tasks_with_problem(self, problems: list[ProblemInfo], n: int, config: dict = None):
        task_list = []
        problem_dict = {p.problem_id: p for p in problems}
        if config:
            try:
                total = 0
                for k, v in config.items():
                    total += v
                assert total == n
            except AssertionError:
                print("Config tasks and param n not matched")
                exit(1)
        else:
            avg = n // len(problems)
            if avg == 0:
                print("[warning] problems count larger than n")
                config = {problems[k].problem_id: 1 for k in range(n)}
            else:
                config = {k.problem_id: avg for k in problems}
                # handle remains
                config[problems[-1].problem_id] = n - avg * (len(problems) - 1)

        for k, v in config.items():
            task_list.extend(self.generate_by_problem(problem_dict[k], v))
        return task_list

    @staticmethod
    def get_distribution(p: float, n: int, mt: float) -> np.core.ndarray:
        tle = int(np.floor(p * n))
        norm = n - tle
        # TODO: more tle appear at first
        r = np.random.uniform(0.5 * mt, 0.9 * mt, norm)
        ts = [mt for _ in range(tle)]
        ts.extend(r)
        ts = np.array(ts)
        np.random.shuffle(ts)
        np.random.shuffle(ts)
        return ts

    def generate_by_problem(self, problem: ProblemInfo, n: int) -> list[JudgeTask]:
        distribution = self.get_distribution(problem.tle_rate, n, problem.limited_time)
        # TODO: memory
        return [JudgeTask(
            tid=i,
            problem_info=problem,
            code="",
            limited_time=problem.limited_time,
            limited_memory=problem.limited_memory,
            exec_time=distribution[i],
            exec_memory=problem.limited_memory
        ) for i in range(n)]


class Dataset:
    def __init__(self, containers: list[Container], problems: list[ProblemInfo], tasks: list[JudgeTask]):
        self.containers = containers
        self.problems = problems
        self.tasks = tasks


class DataManager:
    def __init__(self, path: str = "data/"):
        self.path = path
        self.name_template = "d-{container_count:05d}-{problem_count:05d}-{task_count:06d}"
        self.generator = TaskGenerator()

    def gen_one(self, container_count: int, problem_count: int, task_count: int, save: bool = True):
        # anyone of params should not be 0
        if (container_count and task_count and problem_count) == 0:
            print("Do nothing")
            return
        containers = [
            Container(
                config={
                    "container_id": i,
                    "memory": 2 * 1024 * 1024 * 1024,
                    "machine_id": -1
                }
            ) for i in range(container_count)
        ]
        problems = [
            ProblemInfo(
                problem_id=i,
                tle_rate=float(np.random.rand()),
                mle_rate=0.5,
                limited_memory=1024 * 1024,
                limited_time=200
            ) for i in range(problem_count)
        ]
        tasks = self.generator.generate_n_tasks_with_problem(problems, task_count)
        data = Dataset(containers, problems, tasks)
        # save to local
        dirname = self.name_template.format_map(
            {"container_count": container_count, "problem_count": problem_count, "task_count": task_count})
        self.save(data, dirname)
        return data

    def gen(self, container_count: int, problem_count: int, task_count: int, suit_count: int = 1, save: bool = True):
        if suit_count == 0:
            return
        data_list = []
        for i in range(suit_count):
            data_list.append(self.gen_one(container_count, problem_count, task_count, save))
        return data_list

    def load_one(self, path):
        with open(path, "rb") as f:
            pickle.load(path)

    def load(self, container_count: int, problem_count: int, task_count: int, suit_count: int = 1):
        # check if exists
        dirname = self.name_template.format_map(
            {"container_count": container_count, "problem_count": problem_count, "task_count": task_count})
        count = self.data_count(dirname)
        # generate lacking suits
        if suit_count > count:
            self.gen(container_count, problem_count, task_count, suit_count - count)

        files_to_load = [str(i).zfill(3) for i in range(suit_count)]
        dataset = []
        for f in files_to_load:
            dataset.append(self.load_one(f))
        return dataset

    def data_count(self, dirname):
        current = 0
        path = os.path.join(self.path, dirname)
        if os.path.exists(path):
            file_list = os.listdir(path)
            if len(file_list) != 0:
                file_list.sort()
                try:
                    current = int(file_list[-1])
                except ValueError:
                    print("cannot recognize latest dataset name")
                    exit(1)
                current += 1
        else:
            os.mkdir(path)
        return current

    def save(self, data: Dataset, dirname: str):
        current = self.data_count(dirname)

        with open(os.path.join(self.path, dirname, f"{current:03d}.pic"), "wb") as f:
            pickle.dump(data, f)
