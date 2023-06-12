import yaml
from input.inputelements import InteractiveInputs
from results.response import HOLONErrorReponse, HOLONResponse
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
        return [ie.to_json() for ie in self.interactive_inputs.base.values]

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

    @classmethod
    def load_from_yaml(self, relative_file_path: str = "experiment.yaml"):
        """Load an experiment from a yaml file"""
        # resolve filepath using pathlib as relative import to call location
        fp = Path(inspect.stack()[1].filename).parent / relative_file_path
        with open(fp, "r") as f:
            experiment = yaml.safe_load(f)
        return Experiment(**experiment)

    def interactive_to_df(self, interactive_inputs: List[Dict[str, Any]], uuid: str):
        df = pd.DataFrame(columns=["uuid", "id", "value"])
        for ie in interactive_inputs:
            df.loc[len(df)] = [uuid, ie['interactive_element'], ie['value']]
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

    def run_point(self):
        """Run a single point of the experiment, i.e. a single set of inputs"""
        uuid = str(uuid4())

        response, interactive_elements = self.post()

        if response.status_code == 200:
            result = HOLONResponse(**response.json())
            self._results.append(result.dashboard_results.to_pandas(uuid))
            self._inputs.append(self.interactive_to_df(interactive_elements, uuid))
        else:
            print(response.json())
            result = HOLONErrorReponse(**response.json())

    def run(self, disable_caching: bool = True, enable_sentry_logging: bool = True):
        """Run the experiment, i.e. all points"""
        self.disable_cache = disable_caching
        self.enable_sentry_logging = enable_sentry_logging
        print(f"Starting experiment {self.title}")
        try:
            while True:
                print("Running point")
                self.run_point()
        except StopIteration:
            print("Finished experiment")


