#from optomatic.worker import Worker
#from optomatic.experiment import find_experiment_files, load_experiment_file
from optomatic.plotting import Plotting
import user
import argparse
import sys
import logging
logger = logging.getLogger(__name__)


project_name = "example_multiexperiment"
experiment_name = "rfc:max_features-n_estimators"

p = Plotting(project_name, experiment_name, 
             user.param_space['rfc'], user.param_types['rfc'])

print 'plotting loss vs time'
p.plot_loss_vs_time()


for param in p.param_names:
    print 'plotting loss vs {}'.format(param)
    p.plot_loss_vs_param(param)

print 'plotting loss vs two params'
p.plot_loss_vs_param()

