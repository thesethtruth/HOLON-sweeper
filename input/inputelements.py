from pydantic import BaseModel, validator
from typing import Union, Dict, List


class InteractiveElement(BaseModel):
    id: int


class ContinousInteractiveElement(InteractiveElement):
    value: Union[int, float]


class DiscreteInteractiveElement(InteractiveElement):
    value: str


class DiscreteInteractiveElementSweep(InteractiveElement):
    options: List[str]


class ContinousInteractiveElementSweep(InteractiveElement):
    lower_bound: Union[int, float]
    upper_bound: Union[int, float]
    step: Union[int, float]

    @validator("step")
    def step_must_fit_range(cls, v, values):
        step, upper, lower = v, values["upper_bound"], values["lower_bound"]
        if (upper - lower) % step != 0:
            raise ValueError(
                f"step (={step}) of id {values['id']} must fit in range (=[{upper}, {lower}])])"
            )
        return v


class InteractiveInputs(BaseModel):
    base: Union[
        Dict[str, Union[ContinousInteractiveElement, DiscreteInteractiveElement]], None
    ]
    sweep: Union[
        Dict[
            str,
            Union[ContinousInteractiveElementSweep, DiscreteInteractiveElementSweep],
        ],
        None,
    ]
