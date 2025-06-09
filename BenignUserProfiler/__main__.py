#!/usr/bin/env python3

import argparse
from multiprocessing import cpu_count
from .benign_user_profiler import BenignUserProfiler

def args_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='BenignUserProfiler')
    parser.add_argument('-c', '--config-file', action='store', help='Json config file address.')
    parser.add_argument('-p', '--parallel', action='store_true', help='Run tasks in parallel.')
    parser.add_argument('-w', '--work-hours', nargs='?', const=True, help='Set work hours (e.g. "09:00-17:00") or use default 9am-5pm if no value provided.')
    parser.add_argument('-r', '--randomize', action='store_true', help='Randomize task execution.')
    parser.add_argument('-t', '--threads', action='store', help='Number of threads. default=CPU count')
    return parser


def main():
    parsed_arguments = args_parser().parse_args()
    config_file_address = "./BenignUserProfiler/config.json" if parsed_arguments.config_file is None else parsed_arguments.config_file
    parallel = parsed_arguments.parallel
    work_hours = parsed_arguments.work_hours
    randomize = parsed_arguments.randomize
    number_of_threads = cpu_count() if parsed_arguments.threads is None else int(parsed_arguments.threads)
    
    # Create profiler instance with new parameters
    benign_user_profiler = BenignUserProfiler(
        config_file=config_file_address,
        parallel=parallel,
        work_hours=work_hours,
        randomize=randomize
    )
    benign_user_profiler.run()


if __name__ == "__main__":
    main()