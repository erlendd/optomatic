'''
user.py

This is where the datasets (X, y), the parameter-space and the
objective function are defined.

- X: the features for the data
- y: the labels (targets)
- objective: function that returns a list of scores 
           (mean and standard deviation score will be
            computed in worker.py).
'''


import numpy as np
# from sklearn.cross_validation import cross_val_score
from scipy.stats.distributions import *
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import SVC
from sklearn.datasets import make_classification


X, y = make_classification(100000, n_features=200, n_informative=20)


'''
Define the parameter search space for each classifier. 
If you use ParameterSampler (from scikit-learn) to generate
new candidate points then you can use the statistical
distributions provided by scipy.stats here.
See: http://scikit-learn.org/stable/modules/generated/sklearn.grid_search.ParameterSampler.html 
'''
param_space = {}
param_types = {}

param_space['svc'] = {'C': expon(scale=100), 'gamma': expon(scale=0.1), 'probability': [True], 'kernel': ['linear']}
param_types['svc'] = {'C': 'real', 'gamma': 'real', 'probability': 'int', 'kernel': 'categorical'}

param_space['rfc'] = {'n_estimators': randint(50, 600), 'max_features': [1, 2]}
param_types['rfc'] = {'n_estimators': 'int', 'max_features': 'int'}

'''
clfs maps string-names to a cloneable clf instance.
'''
clfs = {'svc': SVC(), 'rfc': RFC()}


def objective_func(params, clf, X, y):
    '''
    worker.py take one set of params and 
    '''
    clf.set_params(**params)
    scores = cross_val_score(clf, X, y, scoring='log_loss', cv=4, n_jobs=-1)
    scores = -1 * np.array(scores)
    aux_data = [np.mean(score),
                np.std(score),
                np.min(score),
                np.max(score)]
    return list(scores), aux_data
