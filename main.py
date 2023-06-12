from experiment import Experiment

e = Experiment.load_from_yaml("bedrijventerrein.yaml")
e.run(disable_caching=False, enable_sentry_logging=False)

