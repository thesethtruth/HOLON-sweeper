import yaml
from inputelements import (
    InteractiveInputs,
)
import inspect
from pathlib import Path
from pydantic import BaseModel, HttpUrl

import requests as r

ENDPOINT = "/wt/api/nextjs/v2/holon/"


class Experiment(BaseModel):
    scenario_id: str
    title: str
    description: str
    interactive_inputs: InteractiveInputs
    base_url: HttpUrl

    @classmethod
    def load_from_yaml(self, relative_file_path: str = "experiment.yaml"):
        # resolve filepath using pathlib as relative import to call location
        fp = Path(inspect.stack()[1].filename).parent / relative_file_path
        with open(fp, "r") as f:
            experiment = yaml.safe_load(f)
        return Experiment(**experiment)

    def run(self):
        print(f"Running experiment {self.title}")

        response = r.post(
            url=self.base_url + ENDPOINT,
            json={"interactive_elements": [], "scenario": self.scenario_id},
        )
        ## add sentry logging
        ## add caching = False (as cookie)
        
        return response

e = Experiment.load_from_yaml("../empty.yaml")


res = e.run()