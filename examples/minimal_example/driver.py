from sklearn.grid_search import ParameterSampler
from optomatic.jobs import JobsDB
from optomatic.utils import yread
import argparse
from user import get_param_space


def parse_cli():
    parser = argparse.ArgumentParser(
        description='Get new parameters from database and compute their corresponding score.')
    parser.add_argument('--configure',
                        default='config.yaml',
                        help='project configuration file.')
    return parser.parse_args()


def main():
    args = parse_cli()
    config = yread(args.configure)

    # sample parameters
    param_space = get_param_space()
    param_iter = ParameterSampler(param_space, n_iter=config['number_examples'])

    # create MongoDB collection
    jobs = JobsDB(config['project_name'],
                  config['experiment_name'],
                  host=config['MongoDB']['host'],
                  port=config['MongoDB']['port'])
    jobs.create_jobs(None, param_iter)

if __name__ == "__main__":
    main()
