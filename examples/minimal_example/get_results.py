from optomatic.jobs import JobsDB
from optomatic.utils import yread
import argparse


def parse_cli():
    parser = argparse.ArgumentParser(
             description='Fetches and displays the results from the database.')
    parser.add_argument('--configure',
                        default='config.yaml',
                        help='project configuration file.')
    return parser.parse_args()

def main():
    args = parse_cli()
    config = yread(args.configure)
    # connect to collection
    jobs = JobsDB(config['project_name'],
                  config['experiment_name'],
                  host=config['MongoDB']['host'],
                  port=config['MongoDB']['port'])

    jobs.print_job_stats()

    # TODO: need to introduce a Results class to handle this stuff...
    # we'll use the results multiple times, so cache it (TODO: catch OOM)
    completed = list(jobs.get_completed_jobs())
    for idx, trial in enumerate(completed):
        print 'Trial #{}: params: {} / results: {} / run-on: {}'.format(idx, 
               trial['params'], trial['aux_data'], trial['owner'])

if __name__ == "__main__":
    main()

