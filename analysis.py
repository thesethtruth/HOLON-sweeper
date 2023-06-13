import streamlit as st
from results.importer import ResultLoader
import numpy as np
from pathlib import Path
import yaml


with open(Path(__file__).parent / "analysis_config.yaml", "r") as f:
    config = yaml.safe_load(f)
    slider_names = config["slider_names"]


st.title("HOLON sweeper analysis tool")

st.subheader("Load experiment")

experiment_folder = st.text_input(label="Experiment folder", value="experiment_outputs")

if experiment_folder == "experiment_outputs":
    rl = ResultLoader()
else:
    rl = ResultLoader(path=experiment_folder)


experiments = rl.list_experiments()

experiment = st.selectbox(label="Experiment", options=experiments)

experiment_versions = rl.list_experiment_verions(experiment)

experiment_version = st.selectbox(
    label="Experiment version",
    options=experiment_versions,
    format_func=rl.nice_experiment_version,
)

inputs, results, cost_benefit = rl.load_experiment_version_run(
    experiment=experiment, experiment_version=experiment_version
)

# with st.expander("Statistics - experiment overview"):
#     st.write(
#         f"""
#         Total experiments:              {}
#         """
#     )

# with st.expander("Statistics - inputs"):
#     st.write(
#         """
#         This tool allows you to explore the results of the HOLON sweeper.
#         """
#     )

# with st.expander("Statistics - results"):
#     st.write(
#         """
#         This tool allows you to explore the results of the HOLON sweeper.
#         """
#     )





st.subheader("Select output parameters")

level = st.selectbox(
    "Select the level of interest",
    options=["local", "intermediate", "national"],
    format_func=lambda x: x.capitalize(),
)

from results.plotting import plot_kpi

fig = plot_kpi(results, level)

st.plotly_chart(fig, use_container_width=True)



# def dataframe_with_selections(df):
#     df_with_selections = df.copy()
#     df_with_selections.insert(0, "Select", False)
#     edited_df = st.data_editor(
#         df_with_selections,
#         hide_index=True,
#         column_config={"Select": st.column_config.CheckboxColumn(required=True)},
#         disabled=df.columns,
#     )
#     selected_rows = df[edited_df.Select]
#     return selected_rows.uuid


# selection = dataframe_with_selections(inputs)
