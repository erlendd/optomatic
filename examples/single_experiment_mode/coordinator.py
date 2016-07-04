import numpy as np
from sklearn.grid_search import ParameterSampler
from scipy.stats.distributions import *
from optomatic.jobs import JobsDB, param_space_to_experiment_name
from optomatic.experiment import create_jobs, write_experiment_file

import user

project_name = "example_singleexperiment"

features = '111'

for clf_name in user.clfs:

    print "processing {}".format(clf_name)
    # the experiment name is based on the job parameters: this consistent naming
    # allows for re-use of existing experiments when appropriate.
    experiment_name = param_space_to_experiment_name(clf_name, user.param_space[clf_name])

    # set-up the database connection
    jobs = JobsDB(project_name, experiment_name)

    # Set-up the Parameter Generator (here we are using the random sampler from scikit-learn)...
    max_evals = 9
    param_iter = ParameterSampler(user.param_space[clf_name], n_iter=max_evals)

    # Add jobs to the database
    n_jobs = create_jobs(jobs, features, param_iter)

    print "Jobs in project {}, experiment {}".format(project_name, experiment_name)

    # write an .experiment file, which contains the project name and experiment name
    # for the jobs we just created: use this file to batch process those jobs
    # in the multi-experiment mode (see worker.py).
    write_experiment_file(project_name, experiment_name, n_jobs)


print "To run these jobs run ./worker.py in the same directory as the *.experiment files."
