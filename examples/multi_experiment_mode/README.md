# Single-experiment mode
In this mode optomatic runs through a single experiment. New parameters are downloaded from the MongoDB by each worker process. When there are no new parameters the workers wait for new to be added to the database.

## Usage
The dataset, objective-function, model type and model parameter-space are defined in **user.py**. The script **coordinator.py** is responsible for adding jobs to the database, into a collection named based on the machine-learning model and the parameter-space. It also writes out an experiment definition file (with extension .experiment) that contains the project and experiment names. **worker.py** connects to the database and downloads new jobs (i.e. parameters) to run sequentially, it can either read the .experiment file written out by coordinator.py or the project/experiment names can be specified as command-line arguments (see **worker.py --help**).

Step-by-step (after starting MongoDB):

    python ./coordinator.py
    
    python ./worker.py
    
    python ./plot_results.py
    
For distributed processing separate instances of **worker.py** can be run across multiple compute nodes, as long as they can connect to the MongoDB server.

