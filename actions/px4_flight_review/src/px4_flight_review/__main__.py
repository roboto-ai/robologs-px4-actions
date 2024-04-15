import argparse
import os
import io
import pathlib
from jinja2 import Template
from helper import load_ulog_file
from pyulog.px4 import PX4ULog
from db_entry import DBData
from configured_plots import generate_plots
from plotted_tables import get_heading_html
from bokeh.layouts import column
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.io import curdoc
from roboto.domain import actions
from roboto.env import RobotoEnvKey

def process_ulg_file(ulog_file_path, output_folder):
    """Process a single .ulg file to generate and combine Bokeh plots into an HTML report."""
    ulog = load_ulog_file(ulog_file_path)
    px4_ulog = PX4ULog(ulog)
    db_data = DBData()
    vehicle_data = None

    plots = generate_plots(
        ulog,
        px4_ulog,
        db_data,
        vehicle_data,
        None,
        "",
    )

    # Ensure the output directory exists
    output_folder.mkdir(parents=True, exist_ok=True)
    report_filename = pathlib.Path(ulog_file_path).stem + "_report.html"
    report_filepath = output_folder / report_filename

    # Load Jinja HTML template for summary and plots
    dirname = os.path.dirname(__file__)
    j2_template = os.path.join(dirname, 'index.html')

    with open(j2_template) as f:
        template = Template(f.read())

    # Arrange all generated plots into a column
    layout = column(plots)

    # Extract Bokeh HTML components so we can lay out our own file
    # instead of relying on Bokeh's entirely self-generated HTML
    script_bokeh, div_bokeh = components(layout)
    resources_bokeh = CDN.render()

    # Compose HTML file with bokeh plots and additional summary data
    html = template.render(
        resources=resources_bokeh,
        script=script_bokeh,
        plots=div_bokeh,
        title_html=get_heading_html(ulog, px4_ulog, db_data, None),
        hardfault_html=curdoc().template_variables.get("hardfault_html"),
        corrupt_log_html=curdoc().template_variables.get("corrupt_log_html"),
        error_labels_html=curdoc().template_variables.get("error_labels_html"),
        info_table_html=curdoc().template_variables.get("info_table_html"),
        has_position_data=curdoc().template_variables.get("has_position_data"),
        mapbox_api_access_token=os.environ.get("ROBOTO_PARAM_MAPBOX_API_TOKEN"),
        pos_datas=curdoc().template_variables.get("pos_datas"),
        pos_flight_modes=curdoc().template_variables.get("pos_flight_modes"),
    )

    # Save the HTML file
    with io.open(report_filepath, mode="w") as f:
        f.write(html)

def process_ulg_files(input_folder, output_folder):
    """Process all .ulg files within a given folder and its subdirectories."""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".ulg"):
                full_path = os.path.join(root, file)
                relative_path = pathlib.Path(root).relative_to(input_folder)
                output_path = output_folder / relative_path
                process_ulg_file(full_path, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Bokeh plot reports from ULG files."
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        dest="input_dir",
        type=pathlib.Path,
        required=False,
        help="Directory containing input files to process",
        default=os.environ.get(RobotoEnvKey.InputDir.value),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=pathlib.Path,
        required=False,
        help="Directory to which to write any output files to be uploaded",
        default=os.environ.get(RobotoEnvKey.OutputDir.value),
    )

    args = parser.parse_args()

    process_ulg_files(args.input_dir, args.output_dir)
