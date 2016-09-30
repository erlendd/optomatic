from sklearn.grid_search import ParameterSampler
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import SVC
from scipy.stats.distributions import expon, randint
from optomatic.jobs import JobsDB
from optomatic.utils import yread, ywrite
import argparse


def parse_cli():
    parser = argparse.ArgumentParser(
        description='Get new parameters from database and compute their corresponding score.')
    parser.add_argument('--configure',
                        # default='27017',
                        required=True,
                        help='project configuration file.')
    parser.add_argument('--save',
                        # default='27017',
                        required=True,
                        help='configuration for worker.')
    return parser.parse_args()


def chain_dict_keys(param_space):
    name = ''
    param_names = sorted(param_space)
    for key in param_names:
        name += str(key) + "-"
    return name[:-1]


def get_param_space():
    param_space = {}
    param_types = {}

    param_space['svc'] = {'C': expon(scale=100), 'gamma': expon(scale=0.1), 'probability': [True], 'kernel': ['linear']}
    param_types['svc'] = {'C': 'real', 'gamma': 'real', 'probability': 'int', 'kernel': 'categorical'}

    param_space['rfc'] = {'n_estimators': randint(50, 600), 'max_features': [1, 2]}
    param_types['rfc'] = {'n_estimators': 'int', 'max_features': 'int'}

    '''
    clfs maps string-names to a cloneable clf instance.
    '''
    clfs = {'svc': SVC(), 'rfc': RFC()}
    return (clfs, param_space, param_types)


def main():
    args = parse_cli()
    config = yread(args.configure)
    config['experiment_name'] = {}

    clfs, param_space, _ = get_param_space()
    for clf_name in clfs:

        print("processing {}".format(clf_name))
        # sampling max_evals parameters
        param_iter = ParameterSampler(param_space[clf_name], n_iter=config['max_evals'])

        # create the database collection's skeleton
        experiment_name = clf_name + ':' + chain_dict_keys(param_space[clf_name])
        jobs = JobsDB(config['project_name'], experiment_name,
                      host=config['MongoDB']['host'],
                      port=config['MongoDB']['port'])
        jobs.create_jobs(config['features'], param_iter)

        # collect database collection's name
        config['experiment_name'][clf_name] = experiment_name

    # add collection's info to config.
    ywrite(config, args.save)

if __name__ == "__main__":
    main()
