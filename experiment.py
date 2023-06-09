import yaml
from input.inputelements import InteractiveInputs
from results.response import HOLONErrorReponse, HOLONResponse
import inspect
from pathlib import Path
from pydantic import BaseModel, HttpUrl, PrivateAttr
from itertools import product
from typing import Iterable, Dict, List, Tuple, Union
import pandas as pd
from uuid import uuid4
import json

import requests as r

ENDPOINT = "/wt/api/nextjs/v2/holon/"


class Experiment(BaseModel):
    scenario_id: str
    title: str
    description: str
    interactive_inputs: InteractiveInputs
    base_url: HttpUrl
    _sweep_set: Iterable = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._sweep_set = None

    @property
    def current_sweep(self):
        if self.interactive_inputs.sweep is None:
            return None
        else:
            return next(self.sweep_set)

    @property
    def sweep_set(self):
        if self._sweep_set is None:
            self._sweep_set = product(*self.interactive_inputs.sweep.values())
        return self._sweep_set

    @classmethod
    def load_from_yaml(self, relative_file_path: str = "experiment.yaml"):
        # resolve filepath using pathlib as relative import to call location
        fp = Path(inspect.stack()[1].filename).parent / relative_file_path
        with open(fp, "r") as f:
            experiment = yaml.safe_load(f)
        return Experiment(**experiment)

    def post(self):

        # cookies = {"caching": False}
        # params = {"sentry_logging": True} # correct?
        interactive_elements = (
            [
                *[ie.to_json() for ie in self.interactive_inputs.base.values()],
                *[ie.to_json() for ie in self.current_sweep],
            ],
        )
        return json.load(open("fixture/succes_response.json", "r")), interactive_elements
        response = r.post(
            url=self.base_url + ENDPOINT,
            json={
                "interactive_elements": interactive_elements,
                "scenario": 1,
            },
            # cookies=cookies,
            # params=params,
        )

        return response, interactive_elements

    def run_point(self, uuid: str):
        response, interactive_elements = self.post()

        if response.status_code == 200:
            result = HOLONResponse(response.json())
            return result.dashboard_results.to_pandas()
        else:
            result = HOLONErrorReponse(response.json())

    def run(self):
        print("Starting experiment")
        try:
            while True:
                self.run_point(uuid4())
        except StopIteration:
            print("Finished experiment")


e = Experiment.load_from_yaml("base.yaml")
e.run()
