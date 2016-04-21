# About optomatic
Optomatic is a Python library to aid hyperparameter searches for general machine-learning models. The goal of optomatic is to provide a tool that *helps* developers find good hyperparameters for their models in a reasonable time, and to store the stages of their hyperparameter searches in a reproducible (defensible) way.

Optomatic is developed with the following objectives:
* **Performance** Enable parallel-distributed parameter searches across multiple remote machines (e.g. EC2 instances), while storing the results in a central database (MongoDB).
* **Efficiency.** Avoid repetition of calculations, making it easy to extend upon your previous parameter-searches.
* **Simplicity.** The code is actually relatively simple. Use of decorators is restricted only to exception-handling for the pymongo transactions.
* **Extensibility.** The parameter searches are guided by a *generator* that produces new parameter combinations to be tried, and (optionally) *filters* that can remove trial points before they run. You can use ParameterGrid or ParameterSampler from scikit-learn as a generator.

Optomatic is not intended as a set-it-and-leave-it tool for auto-machine-learning, although it could be used as one. 

### Comparison with existing tools
Before writing optomatic I used the excellent [hyperopt](https://github.com/hyperopt/hyperopt) package, which motivated many of the design decisions I took. In particular the use of MongoDB as both a scheduler and as a central datastore for the hyperparameter searches. Unfortunately hyperopt is not longer actively maintained, and there are a number of open issues that may be limiting depending on your level of use. For me the most serious issue is that categorical hyperparamters are converted to integer values before being stored (see [here](https://github.com/hyperopt/hyperopt/issues/243), which can cause difficulties if you want to extend an existing parameter-sweep to include more categories (it can be done if you're careful about the order). 

# Usage
To use optomatic you need to make a very short **driver** code (responsible for deciding which parameters to try) and you need to define a **scoring** function (which computes the metric to optimize, e.g. log-loss, squared-loss). There are examples of both in the examples/ directory.

The **driver** code decides on new parameters to try and adds these to the database, new parameters are suggested using a generator (you can use ParameterGrid or ParameterSampler from scikit-learn). The **worker** connects to the database to find a new set of parameters to try, computes the corresponding score and updates the database with the results. 

#### Running on a single-computer
Start the MongoDB database daemon:

    mkdir ./dbdata/
    mongod --dbpath ./dbdata --port 27017
    # alternatively (Linux): sudo service mongod start

Start the driver code (creates jobs and writes experiment-definition file):

    python ./driver.py

Start the worker code from the same directory (reads experiment-definition file):

    python ./slave.py 

**NB:** there are several command-line parameters for slave.py. These are described with the help switch:

    python ./slave.py --help

# Installation

Optomatic has the following dependencies:
* numpy
* pandas
* scikit-learn
* scipy
* pymongo
These can usually be installed easily using pip. For most users the quick installation below is appropriate.

### Quick install
Clone this repository and use setup.py:
    git clone https://github.com/erlendd/optomatic.git
    sudo python setup.py install

### Manual install
Those wishing to make modifications to this library will want to conduct a manual install by cloning this repository and updating the PYTHONPATH environment variable (Linux and MacOSX).

    git clone https://github.com/erlendd/optomatic.git
    echo "export PYTHONPATH=$PYTHONPATH:$(pwd)/optomatic" >> ~/.bashrc



