from pydantic import BaseModel, validator, PrivateAttr
from typing import Union, Dict, List


class InteractiveElement(BaseModel):
    id: int


class ContinousInteractiveElement(InteractiveElement):
    value: Union[int, float]


class DiscreteInteractiveElement(InteractiveElement):
    value: str


class DiscreteInteractiveElementSweep(InteractiveElement):
    options: List[str]
    _current: Union[int, float] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._current = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        if self._current == len(self.options):
            raise StopIteration
        else:
            result = self.options[self._current]
            self._current += 1
            return DiscreteInteractiveElement(id=self.id, value=result)


class ContinousInteractiveElementSweep(InteractiveElement):
    lower_bound: Union[int, float]
    upper_bound: Union[int, float]
    step: Union[int, float]
    _current: Union[int, float] = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._current = self.lower_bound

    @validator("step")
    def step_must_fit_range(cls, v, values):
        step, upper, lower = v, values["upper_bound"], values["lower_bound"]
        if (upper - lower) % step != 0:
            raise ValueError(
                f"step (={step}) of id {values['id']} must fit in range (=[{upper}, {lower}])])"
            )
        return v

    def __iter__(self):
        return self

    def __next__(self):
        if self._current > self.upper_bound:
            raise StopIteration
        else:
            result = self._current
            self._current += self.step
            return ContinousInteractiveElement(id=self.id, value=result)

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
