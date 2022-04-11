import time
from unittest import TestCase

import numpy as np
import pytest

from model import ProblemInfo
from service.generate_tasks.generate import TaskGenerator, DataManager
import logging

log = logging.getLogger(__name__)


class TestTaskGenerator(TestCase):
    g = TaskGenerator()

    def test_get_distribution(self):
        np.random.seed(None)
        d = self.g.get_distribution(0.4, 100, 2)
        l, t = np.sum(d < 2), np.sum(d == 2)
        # log.info(f"{' '.join([str(i) for i in d])}")

    def test_generate_by_problem(self):
        p = ProblemInfo(
            problem_id=114,
            tle_rate=0.45,
            mle_rate=0.5,
            limited_memory=1000 * 1000,
            limited_time=200
        )
        self.g.generate_by_problem(problem=p, n=100)

    def test_generate_n_tasks(self):
        np.random.seed(None)
        tl = self.g.generate_n_tasks(10, 100)
        self.assertEqual(len(tl), 100)


class TestDataManager(TestCase):
    dm = DataManager()

    def test_gen(self):
        self.dm.gen(4, 10, 100, 1)
