import numpy as np
import pandas as pd
from scipy.stats.stats import pearsonr
from jobs import JobsDB
import matplotlib
matplotlib.use('Agg')
import seaborn as sns; sns.set()
from mpl_toolkits.mplot3d import Axes3D
import math
from sklearn.preprocessing import LabelEncoder
import logging
logger = logging.getLogger(__name__)



class Plotting:

    def __init__(self, project_name, experiment_name, param_space, param_types=None):
        self.project_name = project_name
        self.experiment_name = experiment_name

        # set-up connection to mongodb...
        self.jobs = JobsDB(project_name, experiment_name, param_space=param_space, param_types=param_types)

        # we'll use the results multiple times, so cache it (TODO: catch OOM)
        self.completed = list(self.jobs.get_completed_jobs())

        # set up the parameter-names for the plotters...
        self.param_names = self.jobs.get_param_names()

        self.losses = []
        self.param_values = {}
        for trials in self.completed:

            self.losses.append( trials['loss'] )
            
            for pname in self.param_names:
                pvalues = trials['params'][pname] # the raw values used for ths param
                # check if the parameter needs to be labelized to values... 
                if self.jobs.param_value_encoder[pname]:
                    pvalues = self.jobs.param_value_encoder[pname].transform( pvalues )
                # look for key=pname in the param_values dict, if missing initialise
                # it to and empty list and append the first pvalue. If already present
                # just append pvalue.
                self.param_values.setdefault(pname, []).append( pvalues )
        
        # # some parameters are words, like 'linear' or 'rbf', we can't
        # # find the correlation coefficient between a word and a loss (float),
        # # so we'll use LabelEncoder() from sklearn to map these paramters
        # # to numeric integer values...
        # self.param_value_encoder = {}
        # for name in self.param_names:
        #     self.param_value_encoder[name] = False    

        # self.param_values = {}
        # for name in self.param_names:
        #     self.param_values[name] = []

        # for trials in self.completed: # foreach row
        #     for name in self.param_names: # foreach column
        #         self.param_values[name].append( trials['params'][name] )
        #         # this seems like overkill but it makes sure there are no
        #         # non-numeric parameters that go unnoticed...
        #         if isinstance( trials['params'][name], unicode ):
        #             self.param_value_encoder[name] = LabelEncoder()

        # logging.debug(self.param_value_encoder)
        # for name in self.param_value_encoder:
        #     if self.param_value_encoder[name]:
        #         logging.info('Using LabelEncoder on param: {}'.format(name))
        #         self.param_values[name] = self.param_value_encoder[name].fit_transform(self.param_values[name])

    def mkfilename(self, prefix, extension="png"):
        return "{}_{}-{}.{}".format(prefix, self.project_name, self.experiment_name, extension)

    def plot_loss_vs_time(self):
        best_loss = np.inf
        loss_log = []
        for trial in self.completed:
            trial_loss = float( trial['loss'] )
            if trial_loss < best_loss:
                best_loss = trial_loss
            loss_log.append(best_loss)
        
        sns.plt.plot(loss_log)
        sns.plt.savefig( self.mkfilename('loss_vs_time') )
        sns.plt.close()

    def get_best_two_params(self):
        param_names = self.jobs.get_param_names()
        if len(param_names) == 2:
            return param_names # there can be only two.

        # how much does each parameter correlate with the achieved loss...
        param_losscorr = {}
        for name in self.param_names:
            corr_coef, pval = pearsonr( self.losses, self.param_values[name] )
            logging.info('Correlation of {} with loss: {}'.format(name, corr_coef))
            param_losscorr[name] = abs(corr_coef) # abs, since we don't care about the direction

        sorted_by_corr = sorted(param_losscorr.items(), key=lambda x:x[1], reverse=True)
        best_params  = []
        for i in sorted_by_corr:
            if math.isnan( i[1] ): continue
            best_params.append(i[0])
            if len(best_params) == 2: return best_params
        return best_params
        #return sorted_by_corr[0][0], sorted_by_corr[1][0] # TODO: could be made more general/robust

    def plot_heatmap(self, param1, param2):
        '''
        Method for plotting the loss vs two parameters.
        '''

        dat = []
        for i in range(len(self.losses)):
            dat.append( [self.param_values[param1][i],
                        self.param_values[param2][i],
                           self.losses[i]] )
        logging.info('Plotting 2d heatmap, {} and {} vs loss'.format(param1, param2))
        # must not have duplicates before doing a pivot
        df = pd.DataFrame( dat, columns=[param1, param2, 'loss'] )
        df = df.groupby( [param1, param2], as_index=False ).min()
        df = df.pivot( param1, param2, 'loss' )
        sns.heatmap(df)

    def plot_loss_vs_param(self, params=None):

        if params is None:
            best_params = self.get_best_two_params()
        else:
            if isinstance(params, list):
                best_params = params[-2:]
            else:
                best_params = [params] # just one param

        fig = sns.plt.figure()

        if len(best_params) == 1:
            logging.info("Plotting loss vs. {}".format(best_params[0]))
            ax = fig.add_subplot(111)
            ax.set_ylabel('Log loss')
            ax.set_xlabel( best_params[0] )

            if self.jobs.param_value_encoder[best_params[0]]: ### !!!
                label_names = self.jobs.param_value_encoder[best_params[0]].classes_
                sns.plt.xticks( [0, 1], [label_names[0], label_names[1]] )#self.param_values['kernel'] )
            ax.scatter( self.param_values[best_params[0]], self.losses )

        if len(best_params) == 2:
            self.plot_heatmap(best_params[0], best_params[1])

        plot_filename = "loss_vs_params"
        for param in best_params:
            plot_filename += "-{}".format(param)

        sns.plt.savefig( self.mkfilename(plot_filename) )
        sns.plt.close()


