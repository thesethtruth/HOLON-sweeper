import pandas as pd
from pathlib import Path
import inspect


class ResultLoader():
    def __init__(self, path: Path = None):
        if path is None:
            self.path = Path(inspect.stack()[1].filename).parent / "experiment_outputs"
        else:
            self.path = path

        

    
        
