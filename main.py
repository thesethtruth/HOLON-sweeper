from holonsweeper.experiment import Experiment

e = Experiment.load_from_yaml("single_base.yaml")
e.run(disable_caching=False, enable_sentry_logging=False)

