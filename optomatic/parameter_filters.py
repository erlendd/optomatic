from jobs import JobsDB
import pandas as pd
import logging
logger = logging.getLogger(__name__)

# The filters presented here are mainly to show how to implement one.
#
# NonRepeatingParameterFilter is useful for grid searches where some
# points in the grid have already been calculated, e.g. if you're extending
# upon a previous grid search.
#
# GBParametrFilter is an example of using GradientBoosting with confidence
# intervals to select points that may be more likely to be interesting.
#
# TODO list:
#     a filter that filters out points "close" to existing points

class NonRepeatingParameterFilter:

    def __init__(self, pgenerator, project_name, experiment_name):
        jobsDB = JobsDB(project_name, experiment_name)
        self.params = []
        self.pgenerator = pgenerator
        # Go through all the parameters that pgenerator would make
        # and take out the ones which are already in JobsDB.
        for params in pgenerator:
            if jobsDB.search_by_param(params) is None:
                self.params.append(params)

    def __len__(self):
        return len(self.params)

    def __iter__(self):
        for p in self.params:
            items = sorted(p.items())
            keys, values = zip(*items)
            params = dict(zip(keys, values))
            yield p


class GBParameterFilter:

    def __init__(self, pgenerator, project_name, experiment_name, n_best=0.1, n_samples=None, param_space=None):
        jobsDB = JobsDB(project_name, experiment_name)
        param_values = jobsDB.get_param_values(encode_labels=True)
        df = pd.DataFrame(param_values)

        gb_up = GB(n_estimators=500, learning_rate=0.1,
                    loss='quantile', alpha=0.95, 
                    max_depth=3, max_features=None,
                    min_samples_leaf=9, min_samples_split=9)

        gb_up.fit(df, losses) 

        gb_dn = GB(n_estimators=500, learning_rate=0.1,
                    loss='quantile', alpha=0.05, 
                    max_depth=3, max_features=None,
                    min_samples_leaf=9, min_samples_split=9)

        gb_dn.fit(df, losses) 

        gb = GB(n_estimators=500, learning_rate=0.1,
                    loss='ls',
                    max_depth=3, max_features=None,
                    min_samples_leaf=9, min_samples_split=9)

        gb.fit(df, losses) 

        if hasattr(pgenerator, "__name__"):
            self.pgenerator = pgenerator(param_space, n_samples)
        else:
            self.pgenerator = pgenerator

        trial_params_list = list(self.pgenerator)
        trial_params_df = pd.DataFrame( trial_params_list )
        predicted_loss = gb.predict(trial_params_df)
        predicted_loss_up = gb_up.predict(trial_params_df)
        predicted_loss_dn = gb_dn.predict(trial_params_df)
        idx = np.argsort(predicted_loss_dn)
        sorted_trial_params = np.array(trial_params_list)[idx]

        if n_best >= 1: # actual
            thresh_idx = int(np.round(n_best))
        else: # fraction
            thresh_idx = int( np.round(n_best * len(trial_params_list)) )
         self.params = list(trial_params_list)[:thresh_idx]

    def __len__(self):
        return len(self.params)

    def __iter__(self):
        for p in self.params:
            items = sorted(p.items())
            keys, values = zip(*items)
            params = dict(zip(keys, values))
            yield p




