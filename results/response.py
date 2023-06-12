from pydantic import BaseModel, Json
from typing import Union, Dict
import pandas as pd


class HOLONErrorReponse(BaseModel):
    """Datmodel class to represent an error response from HOLON"""

    error_msg: str
    scenario: Json
    anylogic_outcomes: Union[Json, None]


class DashboardResultSet(BaseModel):
    """Datmodel class to represent a set of dashboard results"""

    sustainability: float
    self_sufficiency: float
    netload: float
    costs: float


class DashboardResults(BaseModel):
    """Datmodel class to represent a set of dashboard results on a single level"""

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
    """Datmodel class to represent a set of cost benefit results"""

    overview: Dict[str, Dict[str, float]]
    detail: Dict[str, Dict[str, Dict[str, float]]]


class HOLONResponse(BaseModel):
    """Datmodel class to represent a succesful response from HOLON"""

    scenario: Dict
    dashboard_results: DashboardResults
    cost_benefit_results: CostBenefitResults
