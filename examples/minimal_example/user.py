from scipy.stats.distributions import randint
from time import sleep


def get_param_space():
    '''
    define parameter space. used by driver.py
    '''
    return {'sleep': randint(1, 5)}


def objective_random_sleep(params):
    '''
    define the tasks. used by worker.py

    It must has a argument named params.
    '''
    sleep(params['sleep'])
    sleep_quality = [2]
    aux_data = ['slept', 'well']
    return sleep_quality, aux_data
