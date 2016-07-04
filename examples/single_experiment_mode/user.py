import numpy as np
from sklearn.cross_validation import cross_val_score
from scipy.stats.distributions import *
from sklearn.ensemble import RandomForestClassifier as RFC

'''
user.py
This is where the datasets (X, y), the parameter-space 
and the objective function are defined for a multi-experiment run. 

X: the features for the data
y: the labels (targets)
objective: function that returns a list of scores 
           (mean and standard deviation score will be
            computed in worker.py).
'''
X = [[1, 2], [1, 3], [2, 4], [2, 1],
     [3, 2], [1, 2], [2, 3], [2, 1],
     [1, 1], [1, 2], [3, 2], [1, 1]]
y = [0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0]

'''
Define the parameter search space for each classifier. 
If you use ParameterSampler (from scikit-learn) to generate
new candidate points then you can use the statistical
distributions provided by scipy.stats here.
See: http://scikit-learn.org/stable/modules/generated/sklearn.grid_search.ParameterSampler.html 
'''
param_space = {}
param_types = {}

param_space['rfc'] = {'n_estimators': [100, 200, 300, 400, 500, 600], 'max_features': [1, 2]}
param_types['rfc'] = {'n_estimators': 'int', 'max_features': 'int'}

'''
clfs maps string-names to a cloneable clf instance.
'''
clfs = {'rfc': RFC()}


'''
clf - the classifier model object e.g. RandomForestClassifier().
clf_params - dictionary of the current parameters.
X - features
y - labels
'''
def objective(clf, clf_params, X, y):
    clf.set_params( **clf_params )
    scores = cross_val_score( clf,
                              X,
                              y,
                              scoring='log_loss',
                              cv=4,
                              n_jobs=-1  )

    # scores will be -ve from log_loss, make +ive...
    scores = -1 * np.array(scores)
    return list(scores)
