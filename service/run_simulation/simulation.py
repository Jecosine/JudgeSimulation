from model import Scheduler
from service.generate_tasks import DataManager

if __name__ == '__main__':
    # setup containers
    dm = DataManager()
    dataset = dm.gen(4, 10, 100, 1)
    s = Scheduler()
