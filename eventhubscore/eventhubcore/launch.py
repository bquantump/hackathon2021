from multiprocessing import Pool, TimeoutError
from eventhubcore import run_server


if __name__ == '__main__':
    # start 4 worker processes
    with Pool(processes=4) as pool:
        pool(run_server, [1,2,3,4])