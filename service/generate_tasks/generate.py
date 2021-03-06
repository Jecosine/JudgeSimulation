import fnmatch
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

    def generate_n_tasks(self, problem_count: int, n: int, config: dict = None) -> list[JudgeTask]:
        problems = [ProblemInfo(
            problem_id=i,
            tle_rate=float(np.random.rand()),
            mle_rate=0.5,
            limited_memory=1000 * 1000,
            limited_time=200
        ) for i in range(problem_count)]
        return self.generate_n_tasks_with_problem(problems, n, config)

    def generate_n_tasks_with_problem(self,
                                      problems: list[ProblemInfo],
                                      n: int,
                                      config: dict = None) -> list[JudgeTask]:
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
    def __init__(self, containers: list[dict], problems: list[ProblemInfo], tasks: list[JudgeTask]):
        self.containers = containers
        self.problems = problems
        self.tasks = tasks


class DataManager:
    def __init__(self, path: str = "data/"):
        self.path = path
        self.name_template = "d-{container_count:05d}-{problem_count:05d}-{task_count:06d}"
        self.generator = TaskGenerator()

    def gen_one(self, container_count: int, problem_count: int, task_count: int, save: bool = True) -> Dataset:
        # anyone of params should not be 0
        if (container_count and task_count and problem_count) == 0:
            print("Do nothing")
            exit(1)
        containers = [
            {
                "container_id": i,
                "memory": 2 * 1024 * 1024 * 1024,
                "machine_id": -1
            } for i in range(container_count)
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
        dirname = self.path_constructor(container_count, problem_count, task_count)
        if save:
            self.save(data, dirname)
        return data

    def gen(self,
            container_count: int,
            problem_count: int,
            task_count: int,
            suit_count: int = 1,
            save: bool = True) -> list[Dataset]:
        if suit_count == 0:
            return []
        data_list = []
        for i in range(suit_count):
            data_list.append(self.gen_one(container_count, problem_count, task_count, save))
        return data_list

    @staticmethod
    def load_one(path) -> Dataset:
        with open(path, "rb") as f:
            data = pickle.load(path)
        return data

    def path_constructor(self,
                         container_count: int,
                         problem_count: int,
                         task_count: int,
                         idx: int = None, ) -> str:
        dirname = self.name_template.format_map(
            {"container_count": container_count, "problem_count": problem_count, "task_count": task_count}
        )
        return os.path.join(self.path, dirname, f"{idx:03d}.pic") if idx is not None \
            else os.path.join(self.path, dirname)

    def load(self,
             container_count: int,
             problem_count: int,
             task_count: int,
             suit_count: int = 1) -> list[Dataset]:
        # check if exists
        dirname = self.path_constructor(container_count, problem_count, task_count)
        count = self.data_count(dirname)
        # generate lacking suits
        if suit_count > count:
            self.gen(container_count, problem_count, task_count, suit_count - count)

        dataset = []
        for i in range(suit_count):
            dataset.append(self.load_one(
                self.path_constructor(container_count, problem_count, task_count, i)
            ))
        return dataset

    @staticmethod
    def data_count(dirname: str) -> int:
        current = 0
        if os.path.exists(dirname):
            file_list = fnmatch.filter(os.listdir(dirname), "*.pic")
            if len(file_list) != 0:
                file_list.sort()
                try:
                    current = int(os.path.splitext(file_list[-1])[0])
                except ValueError:
                    print("cannot recognize latest dataset name")
                    exit(1)
                current += 1
        else:
            os.mkdir(dirname)
        return current

    def save(self, data: Dataset, dirname: str) -> None:
        current = self.data_count(dirname)

        with open(os.path.join(dirname, f"{current:03d}.pic"), "wb") as f:
            pickle.dump(data, f)
