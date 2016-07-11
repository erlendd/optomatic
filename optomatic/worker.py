import numpy as np
import time
from jobs import JobsDB
import logging
logger = logging.getLogger(__name__)

class Worker:

    def __init__(self, project_name, experiment_name, clf, X, y, objective, 
                   host='localhost', port=27017, check_every=1, loop_forever=True):
        self.jobsDB = JobsDB(project_name, experiment_name, host, port)

        self.n_trials = -1 # loop-forever
        if not loop_forever:
            # we're probably running in the multi-experiment mode
            # so once we've computed everything in this experiment
            # we will exit to let the next one run.
            self.n_trials = self.jobsDB.get_queued_jobs().count()

        self.clf = clf # estimator
        self.X = X # X features
        self.y = y # y labels
        self.objective = objective
        self.check_every = check_every # delay in seconds between checking for jobs

    def start_worker(self):
        if self.n_trials > -1:
            logging.info('Worker will close after the {} jobs in this experiment.'.format(self.n_trials))
            for i in range(self.n_trials):
                self.compute()
            # print some stats
            self.jobsDB.print_job_stats()

        else:
            while True:
                self.compute()

    def get_next_params(self):
        job = None
        while job is None:
            job = self.jobsDB.get_next_job_from_queue()
            if job is not None:
                logger.info(job)
            else:
                logger.info('No queued job. Waiting {}s for new jobs...'.format(self.check_every))
                time.sleep(self.check_every)
        return job

    def compute(self):
        job = self.get_next_params()
        clf_params = job['params']
        for p in clf_params:
            # one day, if/when python 3 is ubiquitous, this won't be necessary...
            if isinstance( clf_params[p], unicode ): 
                clf_params[p] = str(clf_params[p])

        scores = self.objective(self.clf, clf_params, self.X, self.y)
        logger.debug("scores from objective: {}".format(scores))

        loss = np.mean(scores)
        std = np.std(scores)

        # then report these results back in the db...
        aux_data = {'loss': loss, 'std': std}
        self.jobsDB.report_job_completion(job['_id'], loss, aux_data=aux_data)



