#from optomatic.worker import Worker
#from optomatic.experiment import find_experiment_files, load_experiment_file
from optomatic.plotting import Plotting
import user
# import argparse
# import sys
from sklearn.grid_search import ParameterSampler
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import SVC
from scipy.stats.distributions import expon, randint
from optomatic.jobs import JobsDB
from optomatic.utils import yread, ywrite
import argparse
import logging
logger = logging.getLogger(__name__)

def parse_cli():
    parser = argparse.ArgumentParser(
        description='Get new parameters from database and compute their corresponding score.')
    parser.add_argument('--configure',
                        # default='27017',
                        required=True,
                        help='project configuration file.')
    parser.add_argument('--dir',
                        # default='27017',
                        required=True,
                        help='configuration for worker.')
    return parser.parse_args()


def main():
    args = parse_cli()
    config = yread(args.configure)
    for clf, db_collection in config['experiment_name'].items():
        p = Plotting(config['project_name'],
                     clf + ':' + db_collection,
                     user.param_space[clf],
                     user.param_types[clf])

    print('plotting loss vs time')
    p.plot_loss_vs_time()

    for param in p.param_names:
        print('plotting loss vs {}'.format(param))
        p.plot_loss_vs_param(param)

    print('plotting loss vs two params')
    p.plot_loss_vs_param()

main()
