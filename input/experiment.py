import yaml
from inputelements import (
    InteractiveInputs,
)
import inspect
from pathlib import Path
from pydantic import BaseModel, HttpUrl, PrivateAttr
from itertools import product
from typing import Iterable

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

    @classmethod
    def load_from_yaml(self, relative_file_path: str = "experiment.yaml"):
        # resolve filepath using pathlib as relative import to call location
        fp = Path(inspect.stack()[1].filename).parent / relative_file_path
        with open(fp, "r") as f:
            experiment = yaml.safe_load(f)
        return Experiment(**experiment)

    def post(self):
        print(f"Running experiment {self.title}")

        # cookies = {"caching": False} # correct?
        # params = {"sentry_logging": True} # correct?

        response = r.post(
            url=self.base_url + ENDPOINT,
            json={
                "interactive_elements": [
                    *[
                        {"interactive_element": ie.id, "value": ie.value}
                        for ie in self.interactive_inputs.base
                    ],
                    *self.current_sweep
                ],
                "scenario": 1,
            },
            # cookies=cookies,
            # params=params,
        )

        return response
    
    @property
    def current_sweep(self):
        if self.interactive_inputs.sweep is None:
            return None
        else:
            return next(self.sweep_set)
    
    @property
    def sweep_set(self):
        if self._sweep_set is None:
            self._sweep_set = product(
                *self.interactive_inputs.sweep.values()
            )
        return self._sweep_set


e = Experiment.load_from_yaml("../base.yaml")