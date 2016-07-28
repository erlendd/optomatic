from optomatic.worker import Worker
from optomatic.utils import yread
from user import objective_random_sleep
import argparse


def parse_cli():
    parser = argparse.ArgumentParser(
        description='Get new parameters from database and compute their corresponding score.')
    parser.add_argument('--configure',
                        default='config.yaml',
                        help='project configuration file.')
    parser.add_argument('--batch-mode',
                        '-b',
                        action='store_true',
                        help="run in batch mode, i.e. exit when there's no jobs")

    args = parser.parse_args()
    args.loop = not args.batch_mode
    return args


def main():
    args = parse_cli()
    config = yread(args.configure)

    w = Worker(config['project_name'],
               config['experiment_name'],
               objective_random_sleep,
               host=config['MongoDB']['host'],
               port=config['MongoDB']['port'],
               loop_forever=args.loop)

    # do the tasks
    w.start_worker()

if __name__ == "__main__":
    main()
