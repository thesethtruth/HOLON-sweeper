import streamlit as st
from results.importer import ResultLoader
import numpy as np


st.title("HOLON sweeper analysis tool")

st.subheader("Load experiment")

experiment_folder = st.text_input(label="Experiment folder", value="experiment_outputs")

if experiment_folder == "experiment_outputs":
    rl = ResultLoader()
else:
    rl = ResultLoader(path=experiment_folder)


experiments = rl.list_experiments()

experiment = st.selectbox(label="Experiment", options=experiments)

experiment_versions = rl.list_experiment_verions(rl.path / experiment)

experiment_version = st.selectbox(
    label="Experiment version",
    options=experiment_versions,
    format_func=rl.nice_experiment_version,
)

inputs, results, cost_benefit = rl.load_experiment_version_run(
    rl.path / experiment / experiment_version
)

st.subheader("Select input parameters")


st.subheader("Select output parameters")

level = st.selectbox(
    "Select the level of interest",
    options=["local", "intermediate", "national"],
    format_func=lambda x: x.capitalize(),
)


for kpi, color in ["sustainability", "self_sufficiency", "netload", "costs"]:
    this_set = (
        results.query("level == @level & kpi == @kpi")
        .drop(["level", "kpi", "uuid"], axis=1)
        .rename(columns={"value": kpi})
        .reset_index(drop=True)
    )


    st.line_chart(this_set, height=300, use_container_width=True, )


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
