import pandas as pd
from pathlib import Path


class ResultLoader:
    def __init__(self, path: Path = None):
        if path is None:
            self.path = Path(__file__).parent.parent / "experiment_outputs"
            self.path = self.path.resolve()
        else:
            self.path = path

    def list_experiments(self):
        return [entry.name for entry in self.path.glob("*") if entry.is_dir()]

    @staticmethod
    def nice_experiment_version(name: str):
        day = pd.to_datetime(name.split("_")[0]).strftime("%Y-%m-%d")
        time = pd.to_datetime(name, format="%Y%m%d_%H%M%S").strftime("%H:%M:%S")

        return " - ".join([day, time])

    def list_experiment_verions(self, experiment_path: Path):
        return [entry.name for entry in experiment_path.glob("*") if entry.is_dir()]

    def list_experiment_versions_nicely(self, experiment_path: Path):
        return [
            self.nice_experiment_version(entry.name)
            for entry in experiment_path.glob("*")
            if entry.is_dir()
        ]

    def load_experiment_version_run(self, experiment_version_path: Path):
        inputs = pd.read_csv(
            experiment_version_path / "inputs.csv", index_col=0, header=0
        )
        results = pd.read_csv(
            experiment_version_path / "results.csv", index_col=0, header=0
        )
        cost_benefit = pd.read_csv(
            experiment_version_path / "cost_benefit.csv", index_col=0, header=0
        )

        return inputs, results, cost_benefit

