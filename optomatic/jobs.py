import pymongo
import time
import socket
import logging
from sklearn.preprocessing import LabelEncoder
logger = logging.getLogger(__name__)


def param_space_to_experiment_name(clf_name, param_space):
    # We do this since, if there are new keys in the parameter space then 
    # it should be considered as a new experiment - otherwise plotting or
    # comparing becomes difficult.
    # Also, must sort the param_space dict for reproducibility...
    name = str(clf_name)
    name += ":"
    param_names = sorted(param_space)
    for key in param_names:
        name += str(key) + "-"
    return name[:-1]  # strip off the last delimiter


# decorator from 
# http://www.arngarden.com/2013/04/29/handling-mongodb-autoreconnect-exceptions-in-python-using-a-proxy/
def safe_mongocall(call):
    def _safe_mongocall(*args, **kwargs):
        for i in range(5):
            try:
                return call(*args, **kwargs)
            except pymongo.errors.AutoReconnect as e:
                waittime = pow(2, i)
                logging.warning('retrying in {}s...'.format(waittime))
                time.sleep(waittime)
        logging.error('Error: Failed operation!  ({})'.format(e))

    return _safe_mongocall

# TODO: with the introduction of param_space in JobsDB, it looks like
#       maybe I should introduce an Experiment or Trials class so that the
#       JobsDB class only deals with the connections side of things.
#       E.g. param_space, setup_value_encoder() would be in Experiment.

# Schema:
#
# | _id | features_in_use | params | status | book_time | refresh_time | loss | aux_data | owner
#
# features_in_use: e.g. str(111) meaning all three features are turned on
# params: dict of the parameters for this clf
# status: 0, 1, 2, 3 (queued, running, completed, failed)
# book_time: when the job was added to the queue
# refresh_time: most recent time that 'owner' phoned-home to the db
# loss: the value of the loss (or utility) that was found
# aux_data: a dict of any addition info, e.g. {'loss': .., 'std': ..}
# owner: the hostname of the machine that is running this job.


class JobsDB:
    def __init__(self,
                 project_name,
                 experiment_name,
                 host='localhost',
                 port=27017,
                 param_space=None,
                 param_types=None):
        self.STATUS_QUEUED = 0
        self.STATUS_RUNNING = 1
        self.STATUS_COMPLETED = 2
        self.STATUS_FAILED = 3

        conn = pymongo.MongoClient()
        self.conn = conn
        self.db = conn[project_name]
        self.collection = self.db[experiment_name]
        self.owner = socket.gethostname()

        self.project_name = project_name
        self.experiment_name = experiment_name

        if param_space is not None:
            self.setup_value_encoder(param_space, param_types)

    @safe_mongocall
    def create_jobs(self, features, param_iter):
        n_success = 0
        for params in param_iter:
            logging.info("Adding to job queue: {}".format(params))
            result = self.add_to_queue(features, params)
            if result is not None:
                n_success += 1
        return n_success

    @safe_mongocall
    def add_to_queue(self, features, params):
        # Adds a job with hyperparameter set 'params' to the collection
        doc = {'status': self.STATUS_QUEUED,
               'book_time': time.time(),
               'refresh_time': None,
               'loss': None,
               'aux_data': None,
               'owner': None,
               'features_in_use': features,
               'params': params}

        result = self.collection.insert(doc)
        logging.debug(result)
        logging.info("New job added to db.")
        return result

    @safe_mongocall
    def get_next_job_from_queue(self, owner=None):
        _owner = self.owner
        if owner is not None:
            _owner = owner
        result = self.collection.find_and_modify(
            {"status": self.STATUS_QUEUED}, {"$set":
                                             {"status": self.STATUS_RUNNING,
                                              "owner": _owner,
                                              "refresh_time": time.time()}})
        return result

    @safe_mongocall
    def report_job_completion(self, jobID, loss, aux_data=None):
        result = self.collection.update_one(
            {"status": self.STATUS_RUNNING,
             "_id": jobID}, {"$set": {"status": self.STATUS_COMPLETED,
                                      "refresh_time": time.time(),
                                      "loss": loss,
                                      "aux_data": aux_data}})
        if result.modified_count == 1:
            return True
        else:
            return False

    def get_param_names(self):
        #result = self.collection.find_one()['params']
        return self.param_names

    @safe_mongocall
    def get_best_run(self, count=1):
        # retrieves the 'count' best runs from the collection (i.e. the current experiment).
        result = self.collection.find({'status': self.STATUS_COMPLETED}).sort(
            {'loss': 1}).limit(count)
        return result

    @safe_mongocall
    def get_orphaned_jobs(self, time_until_old=1800, owner=None):
        # finds all the jobs that last checked-in longer than 'time_until_old' seconds ago
        # optionally limits to just one 'owner'.
        oldtime = time.time() - time_until_old
        needle = {'status': self.STATUS_RUNNING,
                  'refresh_time': {'$lt': time_until_old}}
        if owner is not None:
            if owner == 'self':
                needle['owner'] = self.owner
            else:
                needle['owner'] = owner
        result = self.collection.find(needle)
        return result

    @safe_mongocall
    def search_by_param(self, param):
        needle = {'params': param}
        result = self.collection.find(needle)
        return result

    @safe_mongocall
    def get_all_jobs(self, sort_order=1):
        # by default this returns all jobs in ascending time-order...
        sort_book_order = {'book_time': sort_order}
        result = self.collection.find().sort('book_time', 1)
        return result

    @safe_mongocall
    def get_completed_jobs(self, sort_order=1):
        # by default this returns the completed jobs in ascending time-order...
        needle = {'status': self.STATUS_COMPLETED}
        sort_book_order = {'book_time': sort_order}
        result = self.collection.find(needle).sort('book_time', 1)
        #for i in result: print i
        return result

    @safe_mongocall
    def get_queued_jobs(self, sort_order=1):
        # by default this returns the completed jobs in ascending time-order...
        needle = {'status': self.STATUS_QUEUED}
        sort_book_order = {'book_time': sort_order}
        result = self.collection.find(needle).sort('book_time', 1)
        return result

    def setup_value_encoder(self, param_space, param_types=None):
        self.param_names = []
        self.param_value_encoder = {}
        for param_name in param_space:

            self.param_names.append(param_name)

            # either we passed the types (param_types) or we'll try and infer the types...
            # TODO: we may just make the param_types a required parameter to simplify this bit.
            if param_types is not None:
                if param_types[param_name] == 'categorical':
                    self.param_value_encoder[param_name] = LabelEncoder()
                else:
                    self.param_value_encoder[param_name] = False
            else:  # param_types not explicitly passed: infer which types are categorical
                self.param_value_encoder[
                    param_name] = False  # False, until we find reason otherwise...
                for param_value in param_space[
                        param_name]:  # ...check for that reason now...
                    if isinstance(param_value, unicode) or isinstance(
                            param_value, str):
                        self.param_value_encoder[param_name] = LabelEncoder()

            if self.param_value_encoder[param_name]:
                logging.info('Using LabelEncoder on param: {}'.param_name)
                self.param_value_encoder[param_name].fit(param_space[
                    param_name])

    def get_param_values(self, encode_labels=True):
        losses = []
        param_names = self.get_param_names()
        param_values = {}

        completed = self.get_completed_jobs()

        # set up the param_values dict with a list for-each parameter
        for pname in param_names:
            param_values[pname] = []

        for trials in completed:  # foreach row

            losses.append(trials['loss'])

            for pname in param_names:  # foreach column (param)
                param_values[pname].append(trials['params'][pname])

        # for plotting or fitting, we need to numericalise the word-categorical values...
        if encode_labels:
            for pname in self.param_value_encoder:
                if self.param_value_encoder[pname]:
                    logging.info('Using LabelEncoder on param: {}'.pname)
                    param_values[pname] = self.param_value_encoder[
                        pname].transform(param_values[pname])

        return losses, param_values

    def print_job_stats(self):
        completed_jobs = self.get_completed_jobs()
        all_jobs = self.get_all_jobs()
        orphans = self.get_orphaned_jobs()
        print(' Job Statistics for {} in {}'.format(self.experiment_name,
                                                    self.project_name))
        print('   n_requested  =  {}'.format(all_jobs.count()))
        print('   n_completed  =  {}'.format(completed_jobs.count()))
        print('   n_queued     =  {}'.format(self.get_queued_jobs().count()))
        print('   n_remaining  =  {}'.format((all_jobs.count() -
                                              completed_jobs.count())))
        print('   n_orphaned   =  {}'.format(orphans.count()))
