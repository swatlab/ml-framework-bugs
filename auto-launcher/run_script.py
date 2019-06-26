import os
import logging
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--name', required=True, type=str)
PARSER.add_argument('--type', type=str, choices=['buggy', 'corrected', 'automl'])
PARSER.add_argument('--issue-number', type=str, required=True)


class ModelExperiment(object):
    def __init__(self):
        pass
    def run(self, **kwargs):
        raise NotImplementedError('Not implemented')

def create_model_for_experiment() -> 'ModelExperiment':
    return ModelExperiment()

def experiment_box(name, base_logger):
    # Create a specific logger to file for this experiment
    logger = base_logger.getChild(name)
    experiment_fh = logging.FileHandler('logs/{}'.format(name))
    experiment_fh.setLevel(logging.DEBUG)
    experiment_fh.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    logger.addHandler(experiment_fh)

    m = create_model_for_experiment()
    try:
        logger.info('Starting experiment')
        m.run()
        logger.info('Experiment ran successfully ;)')
    except Exception as e:
        logger.critical(e)
    finally:
        logger.info('Experiment has exited')

def _setup_logging(experiment_name):
    logger = logging.getLogger('base')
    logger.setLevel(logging.DEBUG)
    log_file_handler = logging.FileHandler('logs/all.log')
    log_file_handler.setLevel(logging.DEBUG)
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.CRITICAL)
    formatter = logging.Formatter('%(asctime)s| %(levelname)s | %(name)s | %(message)s')
    log_console_handler.setFormatter(formatter)
    log_file_handler.setFormatter(formatter)
    logger.addHandler(log_file_handler)
    logger.addHandler(log_console_handler)
    return logger

if __name__ == "__main__":
    ARGS = PARSER.parse_args()
    experiment_name = '{}_{}_{}'.format(ARGS.name, ARGS.issue_number, ARGS.type)
    LOGGER = _setup_logging(experiment_name)
    experiment_box(name=experiment_name), base_logger=LOGGER)
