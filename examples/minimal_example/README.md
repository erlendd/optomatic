# Using optomatic for generalised distributed 
This example shows how optomatic can be used to manage the distributed running of general jobs, with the results helpfully collected in the database.
Thanks to Yi Tang (https://github.com/yitang) for contributing this mode.

## Usage
Both the parameters and the workload (objective function) are defined in **user.py**.
Dataset and collection settings are in **config.yaml**.
The script **driver.py** is responsible for adding jobs to the database.
You can see the job status (queued, running, error or finished) using **get_results.py**.

Step-by-step (after starting MongoDB):

    python ./driver.py
    
    python ./worker.py
    
    python ./get_results.py
    
For distributed processing separate instances of **worker.py** can be run across multiple compute nodes, as long as they can connect to the same MongoDB server.

