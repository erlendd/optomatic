import numpy as np
from sklearn.grid_search import ParameterSampler
from scipy.stats.distributions import *
from optomatic.jobs import JobsDB, param_space_to_experiment_name
#from optomatic.experiment import create_jobs, write_experiment_file
from optomatic.utils import yread, ywrite
import user


# we'll manually specify the configuration options here
# but usually you'll want to read this in using yread,
# modify it and write it out to a new worker.yaml file.
# See ../realistic_example for a good example of this.
config = {}
config['MongoDB'] = {'host': 'localhost',
                     'port': 27017}
config['max_evals'] = 9
config['features'] = '111'
config['project_name'] = "example_singleexperiment"

for clf_name in user.clfs:

    print "processing {}".format(clf_name)
    # The experiment name is based on the job parameters: this consistent naming
    # allows for re-use of existing experiments when appropriate.
    experiment_name = param_space_to_experiment_name(clf_name, user.param_space[clf_name])

    # single-experiment mode: only store one experiment per .yaml file
    config['experiment_name'] = {} 
    config['experiment_name'][clf_name] = experiment_name

    # Set-up the Parameter Generator (here we are using the random sampler from scikit-learn)...
    param_iter = ParameterSampler(user.param_space[clf_name], n_iter=config['max_evals'])

    # set-up the database connection
    jobs = JobsDB(config['project_name'], experiment_name,
                  host=config['MongoDB']['host'],
		  port=config['MongoDB']['port'])
    # and add the jobs
    jobs.create_jobs(config['features'], param_iter)

    print "Jobs in project {}, experiment {}".format(config['project_name'], experiment_name)

    # worker.py uses this to find the trials
    ywrite(config, '{}.yaml'.format(experiment_name))
    
    print "To run these jobs run ./worker.py --configure {}.yaml".format(experiment_name)

