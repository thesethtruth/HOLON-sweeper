import pandas as pd
from pathlib import Path
import json


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

    def list_experiment_verions(self, experiment: str):
        return [
            entry.name for entry in (self.path / experiment).glob("*") if entry.is_dir()
        ]

    def list_experiment_versions_nicely(self, experiment: str):
        return [
            self.nice_experiment_version(entry.name)
            for entry in (self.path / experiment).glob("*")
            if entry.is_dir()
        ]

    def load_experiment_version_run(self, experiment: str, experiment_version: str):
        experiment_version_path = self.path / experiment / experiment_version

        inputs = self.load_pd_or_empty(experiment_version_path / "inputs.csv")
        results = self.load_pd_or_empty(experiment_version_path / "results.csv")
        cost_benefit = self.load_pd_or_empty(
            experiment_version_path / "cost_benefit.csv"
        )
        errors = self.load_pd_or_empty(experiment_version_path / "errors.csv")

        return inputs, results, cost_benefit, errors

    def get_scenario_file(self, experiment: str, experiment_version: str, uuid: str):
        experiment_version_path = self.path / experiment / experiment_version

        with open(experiment_version_path / "scenarios" / f"{uuid}.json", "r") as f:
            scenario = f.read()

        return scenario

    @staticmethod
    def cost_benefit_overview(cost_benefit: pd.DataFrame, uuid: str):
        cost_benefit_overview = cost_benefit.set_index("uuid").at[uuid, "overview"]
        cost_benefit_overview = json.loads(cost_benefit_overview.replace("'", '"'))
        cost_benefit_overview = pd.DataFrame(cost_benefit_overview)
        return cost_benefit_overview

    @staticmethod
    def cost_benefit_detail(
        cost_benefit: pd.DataFrame, uuid: str, selected_detail: str
    ):
        cost_benefit_detail = cost_benefit.set_index("uuid").at[uuid, "detail"]
        cost_benefit_detail = json.loads(cost_benefit_detail.replace("'", '"'))
        cost_benefit_detail = cost_benefit_detail[selected_detail]
        cost_benefit_detail = pd.DataFrame(cost_benefit_detail)
        return cost_benefit_detail

    @staticmethod
    def cost_benefit_detail_options(cost_benefit: pd.DataFrame, uuid: str):
        cost_benefit_detail = cost_benefit.set_index("uuid").at[uuid, "detail"]
        cost_benefit_detail = json.loads(cost_benefit_detail.replace("'", '"'))
        return cost_benefit_detail.keys()

    @staticmethod
    def load_pd_or_empty(path: Path):
        try:
            return pd.read_csv(path, index_col=0, header=0)
        except FileNotFoundError:
            return pd.DataFrame()


if __name__ == "__main__":
    rl = ResultLoader()
    experiment = rl.list_experiments()[0]
    experiment_version = rl.list_experiment_verions(experiment)[0]

    inputs, results, cost_benefit, errors = rl.load_experiment_version_run(
        experiment, experiment_version
    )

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
