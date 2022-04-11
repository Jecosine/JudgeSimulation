import os
import argparse
from service.generate_tasks import DataManager
from service.run_simulation import init_argparse

if __name__ == '__main__':
    # check current path
    print(os.getcwd())
    args = init_argparse()
    print(args)
    # setup containers
    dm = DataManager(path=args.data_dir)
    dataset = dm.gen(4, 10, 100, 1)
    print(len(dataset[0].tasks))
