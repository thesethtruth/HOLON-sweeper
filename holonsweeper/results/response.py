from pydantic import BaseModel
from typing import Union, Dict
import pandas as pd
from pathlib import Path
import json


class HOLONErrorReponse(BaseModel):
    """Datamodel class to represent an error response from HOLON"""

    error_msg: str
    scenario: dict
    anylogic_outcomes: Union[dict, None]

    def write_scenario(self, path: Path, uuid: str):
        """Write the scenario to a json file"""
        path = path / f"{uuid}.json"
        with open(path, "w") as f:
            json.dump(self.scenario, f)

    def write_anylogic(self, path: Path, uuid: str):
        """Write the anylogic outcomes to a json file"""
        path = path / f"{uuid}.json"
        if self.anylogic_outcomes is not None:
            with open(path, "w") as f:
                json.dump(self.anylogic_outcomes, f)


class DashboardResultSet(BaseModel):
    """Datamodel class to represent a set of dashboard results"""

    sustainability: float
    self_sufficiency: float
    netload: float
    costs: float


class DashboardResults(BaseModel):
    """Datamodel class to represent a set of dashboard results on a single level"""

    local: DashboardResultSet
    intermediate: DashboardResultSet
    national: DashboardResultSet

    def to_pandas(self, uuid: str):
        df = pd.DataFrame(columns=["uuid", "level", "kpi", "value"])
        for level, kpi_set in self:
            for name, value in kpi_set:
                df.loc[len(df)] = [uuid, level, name, value]

        return df


class CostBenefitResults(BaseModel):
    """Datamodel class to represent a set of cost benefit results"""

    overview: Dict[str, Dict[str, float]]
    detail: Dict[str, Dict[str, Dict[str, float]]]

    def to_pandas(self, uuid: str):
        """Convert the results to a pandas dataframe"""
        return pd.DataFrame(
            columns=["uuid", "overview", "detail"],
            data=[[uuid, self.overview, self.detail]],
        )


class HOLONResponse(BaseModel):
    """Datamodel class to represent a succesful response from HOLON"""

    scenario: dict
    dashboard_results: DashboardResults
    cost_benefit_results: CostBenefitResults

    def write_scenario(self, path: Path, uuid: str):
        """Write the scenario to a json file"""
        path = path / f"{uuid}.json"
        with open(path, "w") as f:
            json.dump(self.scenario, f)
