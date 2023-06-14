This is a repo that contains only a tiny utility script to run various scenarios on holontool.nl. Allows you to quickly assess results and tweak your model or settings to achieve your dreams!

### How to have great time
1. Install using `poetry install`
2. Activate the environment in your IDE
3. Define an experiment in a `yaml` file format (for an example see `base.yaml`)
4. Change `main.py` to use the `yaml` you just defined
5. Use `python main.py` to run the experiment
6. Analyse results interactively using `streamlit run analysis.py`