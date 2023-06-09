from pydantic import BaseModel, Json
from typing import Union, Dict
import pandas as pd

class HOLONErrorReponse(BaseModel):
    error_msg: str
    scenario: Json
    anylogic_outcomes: Union[Json, None]


class DashboardResultSet(BaseModel):
    sustainability: float
    self_sufficiency: float
    netload: float
    costs: float

class DashboardResults(BaseModel):
    local: DashboardResultSet
    intermediate: DashboardResultSet
    national: DashboardResultSet

    def to_pandas(self):
        df = pd.DataFrame(columns=['level', 'kpi', 'value'])
        for level, kpi_set in self:
            for name, value in kpi_set:
                df.loc[len(df)] = [level, name, value]
        
        return df

class CostBenefitResults(BaseModel):
    overview: Dict[str, Dict[str, float]]
    detail: Dict[str, Dict[str, Dict[str, float]]]

class HOLONResponse(BaseModel):
    scenario: Dict
    dashboard_results: DashboardResults
    cost_benefit_results: CostBenefitResults