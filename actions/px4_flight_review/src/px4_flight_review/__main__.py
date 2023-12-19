import argparse
import os
import pathlib
from bokeh.plotting import output_file, save
from helper import load_ulog_file
from pyulog.px4 import PX4ULog
from db_entry import DBData
from configured_plots import generate_plots
import re
from bokeh.io import export_png
import img2pdf
from roboto.domain import actions


def extract_plot_html(file_path):
    """Extracts the HTML content of a Bokeh plot from a saved file."""
    with open(file_path, 'r') as file:
        content = file.read()
        plot_html = re.search(r'(?<=<body>).*(?=</body>)', content, re.DOTALL).group()
    return plot_html


def extract_head_html(file_path):
    """Extracts the HTML content for Bokeh resources from the <head> section."""
    with open(file_path, 'r') as file:
        content = file.read()
        head_html = re.search(r'(?<=<head>).*(?=</head>)', content, re.DOTALL).group()
    return head_html


def process_ulg_file(ulog_file_path, output_folder, save_pdf):
    """Process a single .ulg file to generate and combine Bokeh plots into an HTML report."""
    ulog = load_ulog_file(ulog_file_path)
    px4_ulog = PX4ULog(ulog)
    db_data = DBData()
    vehicle_data = None  # You will need to determine how to set this

    log_id = "av"
    link_to_3d_page = '3d?log=' + log_id
    link_to_pid_analysis_page = '?plots=pid_analysis&log=' + log_id

    plots = generate_plots(ulog, px4_ulog, db_data, vehicle_data, link_to_3d_page, link_to_pid_analysis_page)

    # Ensure the output directory exists
    output_folder.mkdir(parents=True, exist_ok=True)
    report_filename = pathlib.Path(ulog_file_path).stem + '_report.html'
    report_filepath = output_folder / report_filename

    # Save individual plots as PNG and create HTML content
    combined_html_content = ""
    png_files = []  # List to store paths of PNG files

    for i, plot in enumerate(plots):
        try:
            if save_pdf:
            # Export plot as PNG
                png_filename = report_filepath.with_suffix(f'.{i}.png')
                export_png(plot, filename=png_filename)
                png_files.append(png_filename)

            # Create HTML content (optional if you only need the PDF)
            plot_file = report_filepath.with_suffix(f'.{i}.html')
            output_file(plot_file)
            save(plot)

            if i == 0:  # Extract head from first plot
                combined_html_content += f"<html><head>{extract_head_html(plot_file)}</head><body>"
            combined_html_content += extract_plot_html(plot_file)

            # Delete the individual plot file
            plot_file.unlink(missing_ok=True)
        except Exception as e:
            print(f"Error processing plot {i}: {e}")

    combined_html_content += "</body></html>"

    # Save as HTML (optional if you only need the PDF)
    with open(report_filepath, 'w') as file:
        file.write(combined_html_content)
    print(f"Report generated: {report_filepath}")

    if save_pdf:
        # Combine PNG files into a single PDF
        pdf_filename = report_filepath.with_suffix('.pdf')
        with open(pdf_filename, "wb") as f:
            f.write(img2pdf.convert(png_files))
        print(f"PDF report generated: {pdf_filename}")

        # Optional: Cleanup PNG files after PDF creation
        for png_file in png_files:
            png_file.unlink()


def process_ulg_files(input_folder, output_folder, save_pdf):
    """Process all .ulg files within a given folder and its subdirectories."""
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".ulg"):
                full_path = os.path.join(root, file)
                relative_path = pathlib.Path(root).relative_to(input_folder)
                output_path = output_folder / relative_path
                process_ulg_file(full_path, output_path, save_pdf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Bokeh plot reports from ULG files.')
    parser.add_argument(
        "-i",
        "--input-dir",
        dest="input_dir",
        type=pathlib.Path,
        required=False,
        help="Directory containing input files to process",
        default=os.environ.get(actions.InvocationEnvVar.InputDir.value),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=pathlib.Path,
        required=False,
        help="Directory to which to write any output files to be uploaded",
        default=os.environ.get(actions.InvocationEnvVar.OutputDir.value),
    )

    parser.add_argument(
        "--save-pdf",
        action="store_true",
        required=False,
        help="Set True to save PDF reports",
        default=(os.environ.get("ROBOTO_PARAM_SAVE_PDF") == "True"),
    )

    args = parser.parse_args()

    process_ulg_files(args.input_dir, args.output_dir, args.save_pdf)

