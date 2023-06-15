import streamlit as st
from results.importer import ResultLoader
import numpy as np
from pathlib import Path
import yaml

with open(Path(__file__).parent / "analysis_config.yaml", "r") as f:
    config = yaml.safe_load(f)
    slider_names = config["slider_names"]


st.title("HOLON sweeper analysis tool")

st.subheader("Experiment to load")

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

inputs, results, cost_benefit, errors = rl.load_experiment_version_run(
    experiment=experiment, experiment_version=experiment_version
)

st.success(
    f"""
    #### Statistics - experiment overview
    Total experiments:    **{results.uuid.unique().shape[0]}** \n
    Total errors:         **{errors.shape[0]}**
    """
)

# TODO
# Statistics of inputs
# Statistics of results

st.subheader("Experiment outcomes")

level = st.selectbox(
    "Select the level of interest",
    options=["local", "intermediate", "national"],
    format_func=lambda x: x.capitalize(),
)

sort_by = st.selectbox(
    "Sort by (ascending)",
    options=results.kpi.unique(),
    format_func=lambda x: x.replace("_", " ").capitalize(),
)

from results.plotting import plot_kpi

fig = plot_kpi(results, level, sort_by=sort_by)

from streamlit_plotly_events import plotly_events

selected_point = plotly_events(fig, "click")

if selected_point:
    uuid = selected_point[0]["x"]

    st.subheader(f"Selected UUID: {uuid}")

    selected_inputs = inputs.query("uuid == @uuid").drop("uuid", axis=1)
    selected_inputs["slider_name"] = selected_inputs["id"].map(slider_names)
    selected_inputs = selected_inputs.set_index("slider_name")

    st.dataframe(selected_inputs)

    st.subheader("Cost benefit analysis")

    with st.expander("Cost benefit - overview"):
        st.dataframe(rl.cost_benefit_overview(cost_benefit, uuid))

    with st.expander("Cost benefit - detail"):
        options = rl.cost_benefit_detail_options(cost_benefit, uuid)
        detail = st.selectbox("Select subgroup", options)

        st.dataframe(rl.cost_benefit_detail(cost_benefit, uuid, detail))

    st.subheader("Source files")

    # button to download file
    st.download_button(
        label="Download scenario input file",
        data=rl.get_scenario_file(experiment, experiment_version, uuid),
        file_name="scenario.json",
        mime="json",
    )


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
