from optomatic.worker import Worker
from sklearn.cross_validation import cross_val_score
import numpy as np
import user
import argparse
import logging
import yaml
logger = logging.getLogger(__name__)


def parse_cli():
    parser = argparse.ArgumentParser(
        description='Get new parameters from database and compute their corresponding score.')
    parser.add_argument('--configure',
                        # default='27017',
                        required=True,
                        help='project configuration file.')
    parser.add_argument('--batch-mode',
                        '-b',
                        action='store_true',
                        help="write in batch mode, i.e. exit when there's no jobs")

    args = parser.parse_args()
    args.loop = not args.batch_mode
    return args


def main():
    args = parse_cli()

    with open(args.configure, 'r') as f:
        config = yaml.load(f)

    for clf_name, db_collection in config['experiment_name'].items():
        clf = user.clfs[clf_name]
        w = Worker(config['project_name'], db_collection,
                   user.objective_func, host=config['MongoDB']['host'],
                   port=config['MongoDB']['port'],
                   loop_forever=args.loop)
        w.start_worker(clf=clf, X=user.X, y=user.y)
main()
