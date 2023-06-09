from response import HOLONResponse
import json
import pandas as pd

h = HOLONResponse(**json.load(open("../fixture/succes_response.json", 'r')))


df = h.dashboard_results.to_pandas()


