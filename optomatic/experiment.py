import json
import glob
import logging
logger = logging.getLogger(__name__)

def create_jobs(jobs_connection, features, param_iter):
    n_success = 0
    for params in param_iter:
        logging.info("Adding to job queue: {}".format(params))
        result = jobs_connection.add_to_queue(features, params)
        if result is not None:
            n_success += 1
    return n_success


def write_experiment_file(project_name, experiment_name, size=None):
    data = { 'project': project_name, 'experiment': experiment_name, 'size': size }
    fn = "{}-{}.json".format(project_name, experiment_name)
    with open(fn, 'w') as f:
        json.dump(data, f)

def load_experiment_file(fn):
    file = open(fn, 'r')
    j = json.load(file)
    file.close()
    return j

   
def find_experiment_files():
    files = []
    for file in glob.glob("*.json"):
        files.append(file)
    return files
