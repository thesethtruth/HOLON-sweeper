import yaml
from .inputs.inputelements import InteractiveInputs
from .results.response import HOLONErrorReponse, HOLONResponse
import inspect
from pathlib import Path
from itertools import product
from typing import Iterable, Dict, List, Tuple, Union, Any
import pandas as pd
from uuid import uuid4
import json

import requests as r

ENDPOINT = "/wt/api/nextjs/v2/holon/"


class Experiment:
    """Class to represent an experiment"""

    def __init__(
        self,
        scenario_id: str,
        title: str,
        description: str,
        interactive_inputs: InteractiveInputs,
        base_url: str,
        disable_cache: bool = True,
        enable_sentry_logging: bool = True,
    ) -> None:
        self.scenario_id = scenario_id
        self.title = title
        self.description = description
        self.interactive_inputs = InteractiveInputs(**interactive_inputs)
        self.base_url = base_url
        self.disable_cache = disable_cache
        self.enable_sentry_logging = enable_sentry_logging

        self._results = []
        self._inputs = []
        self._cost_benefit = []
        self._errors = {}
        self._sweep_set: Iterable = None
        self._single_sweep: bool = False

    @property
    def current_sweep(self):
        """Return the current sweep set as a list of dicts"""
        if self._single_sweep == True:
            raise StopIteration
        if self.interactive_inputs.sweep is None:
            self._single_sweep = True
            return []
        else:
            return [ie.to_json() for ie in next(self.sweep_set)]

    @property
    def base(self):
        """Return the base set as a list of dicts"""
        if self.interactive_inputs.base is None:
            return []
        return [ie.to_json() for ie in self.interactive_inputs.base.values()]

    @property
    def sweep_set(self):
        """Return the sweep set as an iterable of tuples of values"""
        if self._sweep_set is None:
            self._sweep_set = product(*self.interactive_inputs.sweep.values())
        return self._sweep_set

    @property
    def results(self):
        """Return results as a pandas dataframe"""
        return pd.concat(self._results)

    @property
    def inputs(self):
        """Return inputs as a pandas dataframe"""
        return pd.concat(self._inputs)

    @property
    def cost_benefit(self):
        """Return cost benifit as a pandas dataframe"""
        return pd.concat(self._cost_benefit)

    @property
    def errors(self):
        """Return errors as a pandas dataframe"""
        return pd.DataFrame.from_dict(self._errors, orient="index", columns=["error_msg"])

    @classmethod
    def load_from_yaml(self, relative_file_path: str = "experiment.yaml"):
        """Load an experiment from a yaml file"""
        # resolve filepath using pathlib as relative import to call location
        self.config_path = Path(inspect.stack()[1].filename).parent / relative_file_path
        with open(self.config_path, "r") as f:
            experiment = yaml.safe_load(f)
        return Experiment(**experiment)

    def interactive_to_df(self, interactive_inputs: List[Dict[str, Any]], uuid: str):
        df = pd.DataFrame(columns=["uuid", "id", "value"])
        for ie in interactive_inputs:
            df.loc[len(df)] = [uuid, ie["interactive_element"], ie["value"]]
        return df

    def post(self):
        """Post the current set of inputs to the HOLON API"""

        if self.disable_cache:
            cookies = {"caching": "false"}
        else:
            cookies = {"caching": "true"}

        if self.enable_sentry_logging:
            params = {"sentry_logging": True}  # TODO correct?
        else:
            params = {"sentry_logging": False}

        interactive_elements = [
            *self.base,
            *self.current_sweep,
        ]

        response = r.post(
            url=self.base_url + ENDPOINT,
            json={
                "interactive_elements": interactive_elements,
                "scenario": 1,
            },
            cookies=cookies,
            params=params,
        )

        return response, interactive_elements

    def store_results(
        self,
        result: Union[HOLONResponse, HOLONErrorReponse],
        interactive_elements: List[Dict[str, Any]],
    ):
        """Store the results of a single point"""
        uuid = str(uuid4())

        # Both cases have inputs and an scenario file
        result.write_scenario(self.scenario_folder, uuid)
        self._inputs.append(self.interactive_to_df(interactive_elements, uuid))

        if isinstance(result, HOLONResponse):
            # only if the result is a success do we have dashboard and cost benefit results
            self._results.append(result.dashboard_results.to_pandas(uuid))
            self._cost_benefit.append(result.cost_benefit_results.to_pandas(uuid))
        else:
            # if error, error message & anylogic response JSON
            result.write_anylogic(self.anylogic_folder, uuid)
            self._errors.update({uuid: result.error_msg})

    def initiate_experiment(self):
        """creates a folder for the experiment and subfolders for anylogic and scenario files"""

        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        self.experiment_folder = (
            self.config_path.parent / "experiment_outputs" / f"{self.title}" / f"{timestamp}"
        )
        self.scenario_folder = self.experiment_folder / "scenario"
        self.anylogic_folder = self.experiment_folder / "anylogic"
        self.experiment_folder.mkdir(parents=True, exist_ok=True)
        self.scenario_folder.mkdir(parents=True, exist_ok=True)
        self.anylogic_folder.mkdir(parents=True, exist_ok=True)

    def run_point(self):
        """Run a single point of the experiment, i.e. a single set of inputs"""

        response, interactive_elements = self.post()

        if response.status_code == 200:
            result = HOLONResponse(**response.json())
        else:
            result = HOLONErrorReponse(**response.json())

        self.store_results(result, interactive_elements)

    def write_results_to_csv(self):
        """Write the results to csv files"""
        self.results.to_csv(self.experiment_folder / "results.csv")
        self.inputs.to_csv(self.experiment_folder / "inputs.csv")
        self.cost_benefit.to_csv(self.experiment_folder / "cost_benefit.csv")
        self.errors.to_csv(self.experiment_folder / "errors.csv")

    def run(self, disable_caching: bool = True, enable_sentry_logging: bool = True):
        """Run the experiment, i.e. all points"""
        self.disable_cache = disable_caching
        self.enable_sentry_logging = enable_sentry_logging
        print(f"Starting experiment {self.title}")
        self.initiate_experiment()
        try:
            while True:
                print("Running point")
                self.run_point()
        except StopIteration:
            print("Finished experiment")

        self.write_results_to_csv()