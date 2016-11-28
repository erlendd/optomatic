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
    parser.add_argument('--conf',
                        required=True,
                        help='project configuration file.')

    args = parser.parse_args()
    return args


def main():
    args = parse_cli()

    with open(args.conf, 'r') as f:
        config = yaml.load(f)

    for clf_name, db_collection in config['experiment_name'].items():
        clf = user.clfs[clf_name]

	# call worker with loop_forever = True, for single-experiment mode.
	# In this mode this worker will not exit, and will continually check
	# for new jobs in the current experiment (db_collection).
	# Single-experiment mode is therefore not (yet) appropriate for 
	# running jobs from multiple different experiments.
        w = Worker(config['project_name'], db_collection,
                   user.objective, host=config['MongoDB']['host'],
                   port=config['MongoDB']['port'],
                   loop_forever=True)
        w.start_worker(clf=clf, X=user.X, y=user.y)
main()
