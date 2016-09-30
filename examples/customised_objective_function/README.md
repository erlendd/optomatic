# Multi-experiment mode
In this mode optomatic runs through multiple experiments (batch processing), downloading new parameters from the MongoDB server. When there are no new parameters in a given experiment the worker process will move to the next experiment until all defined experiments have been computed.

## Usage
The dataset, objective-function, model type and model parameter-space are defined in **user.py**. The script **coordinator.py** is responsible for adding jobs to the database, into a collection named based on the machine-learning model and the parameter-space. It also writes out an experiment definition file for each set of model/parameter pairs (with extension .experiment) that contains the project and experiment names. In multi-experiment mode it is recommended to use the .experiment files to manage the worker processes. **worker.py** connects to the database and downloads new jobs (i.e. parameters) to run sequentially, it reads the .experiment file written out by coordinator.py to know where to look for new jobs.

Step-by-step (after starting MongoDB):

    python ./coordinator.py
    
    python ./worker.py
    
    python ./plot_results.py
    
For distributed processing separate instances of **worker.py** can be run across multiple compute nodes, as long as they can connect to the MongoDB server.

