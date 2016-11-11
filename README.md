![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)
[![License](https://img.shields.io/badge/license-MIT%20License-brightgreen.svg)](https://opensource.org/licenses/MIT)
[![Join the chat at https://gitter.im/optomatic/Lobby](https://badges.gitter.im/optomatic/Lobby.svg)](https://gitter.im/optomatic/Lobby)

# About optomatic
Optomatic is a Python library to aid hyperparameter searches for general machine-learning models. The goal of optomatic is to provide a tool that helps developers find good hyperparameters for their models in a reasonable time, and to store the stages of their hyperparameter searches in a reproducible (and defensible) way.

Optomatic has been developed with the following objectives:
* **Performance** Enable parallel-distributed parameter searches across multiple remote machines (e.g. EC2 instances, University clusters and desktop computers), while storing the results in a central MongoDB database.
* **Efficiency.** Avoid repetition of calculations, making it easy to extend upon your previous parameter-searches.
* **Simplicity.** The code is actually relatively simple, for instance use of decorators is currently restricted only to exception-handling for the pymongo transactions.
* **Extensibility.** The parameter searches are guided by a *generator* that produces new parameter combinations to be tried, and (optionally) *filters* that can remove trial points before they run. The generators follow the style of ParameterGrid and ParameterSampler from scikit-learn, so those can be used directly or modified to your needs.

#### Comparison with existing tools
Many of the design decisions taken in the development of optomatic were influenced by the excellent [hyperopt](https://github.com/hyperopt/hyperopt) and [optunity](https://github.com/claesenm/optunity) Python packages. In particular the use of MongoDB, both as a scheduler and as a central datastore for the parameter searches came from hyperopt. Unfortunately hyperopt is [no longer maintained](https://github.com/hyperopt/hyperopt/issues/237#issuecomment-139573968), and hasn't been updated to support MongoDB version 3. 
Optunity supports the widest variety of distinct optimizers for real-valued parameters, however, optomatic offers a a range of different parameter types in addition to continuous real-values, and distributed running of worker processes.

Optomatic divides the problem of hyperparameter searching into two parts:

1. a parameter generator, which suggests new candidate parameters to try,
2. an optional parameter filter, that takes those candidate parameters and filters out (discards) some according to a rule.

Currently you can use ParameterSampler or ParameterGrid (from scikit-learn) as generators. 
There are also two filters available: NonRepeatingFilter, which discard candidate parameters which have already been tried, and GBFilter, which discards candidate parameters when their (gradient boosting) *predicted* score is poor.

**Random search.** The most common metric for evaluating the performance of hyperparameter search methods in the academic literature is the number of iterations, however this ignores the time taken per iteration. 
Many advanced search methods have a high computational overhead that can offset or even outweigh their benefits when compared with much simpler methods. For this reason, and [several](http://blog.dato.com/how-to-evaluate-machine-learning-models-part-4-hyperparameter-tuning) [others](http://www.jmlr.org/papers/v13/bergstra12a.html), random search is the preferred optimizer in optomatic. 

# Usage
To use optomatic you need to make a very short **driver** code (responsible for deciding which parameters to try) and you need to define a **scoring** (or objective) function, which computes the metric to optimize (e.g. log-loss or squared-loss). There are examples of both in the examples/ directory (more elaborate examples on real-world datasets will follow).

The **driver** code decides on new parameters to try and adds these to the database, new parameters are suggested using a generator (and an optional filter). A **worker** connects to the database to find a new set of parameters to try, computes the corresponding score and updates the database with the results. 

#### Running on a single computer
Start the MongoDB database daemon:

    mkdir ./dbdata/
    mongod --dbpath ./dbdata --port 27017
    # alternatively in Linux you can usually type: sudo service mongod start

Start the driver code (creates jobs and writes experiment-definition file):

    python ./driver.py

Start the worker code from the same directory (reads experiment-definition file):

    python ./worker.py 

**NB:** there are several command-line parameters for worker.py. These are described with the help switch:

    python ./worker.py --help

# Installation

Optomatic has the following dependencies:
* numpy
* pandas
* scikit-learn
* scipy
* pymongo

These can be installed easily using pip. For most users the quick installation below is appropriate.

#### Quick install
Clone this repository and use setup.py:

    git clone https://github.com/erlendd/optomatic.git
    cd optomatic
    sudo pip install .
    *OR*
    sudo python setup.py install

#### Manual install
Those wishing to make modifications to this library will want to conduct a manual install by cloning this repository and updating the PYTHONPATH environment variable (Linux and MacOSX).

    git clone https://github.com/erlendd/optomatic.git
    echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/optomatic" >> ~/.bashrc



