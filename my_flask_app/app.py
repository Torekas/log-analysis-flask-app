import io
import os

import matplotlib
import textwrap
import numpy as np
import pandas as pd
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, url_for)
from log_processor import run_log_processing

matplotlib.use("Agg")
from typing import Dict, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from orchestrator import Orchestrator
from tabulate import tabulate
from collections import defaultdict

app = Flask(__name__)

# Global variables for user parameters and orchestrator instance
user_params: Dict[str, Optional[str]] = {
    "test_directory": None,
    "specific_value": None,
    "distance_column": None,
    "status_column": None,
}

distance_targets: Dict[int, int] = {
    100: 100,
    150: 150,
    200: 200,
    250: 250,
}  # Add more if needed
orchestrator: Optional[Orchestrator] = None


@app.route("/")
def index() -> str:
    """
    Render the main index page.

    :returns: HTML content for the main page.
    :rtype: str
    """
    if orchestrator is None or len(orchestrator.point_list) == 0:
        return render_template("no_data.html")
    return render_template("index.html")


@app.route("/process_logs", methods=["GET", "POST"])
def process_logs() -> str:
    """
    Process log files into CSV and SQLite database.

    :returns: HTML content for the result of log processing.
    :rtype: str
    """
    if request.method == "POST":
        log_dir = request.form.get("log_dir", "./logs")
        output_dir = request.form.get("output_dir", "./output")
        db_file = request.form.get("db_file", "./logs_data.db")

        success = run_log_processing(
            log_dir=log_dir, output_dir=output_dir, db_file=db_file
        )
        if success:
            message = "Logs processed successfully. CSV files and database created."
        else:
            message = "Failed to process logs."

        return render_template("process_logs.html", message=message)
    return render_template("process_logs.html")


@app.route("/config", methods=["GET", "POST"])
def config() -> str:
    """
    Configure user parameters for analysis.

    :returns: HTML content for the configuration page.
    :rtype: str
    """
    if request.method == "POST":
        user_params["test_directory"] = request.form.get("test_directory")
        user_params["specific_value"] = request.form.get("specific_value")
        user_params["distance_column"] = request.form.get("distance_column")
        user_params["status_column"] = request.form.get("status_column")

        if (
            not user_params["test_directory"]
            or not user_params["specific_value"]
            or not user_params["distance_column"]
            or not user_params["status_column"]
        ):
            return render_template(
                "config.html", error="All fields are required.", user_params=user_params
            )

        global orchestrator
        orchestrator = Orchestrator(
            user_params["test_directory"],
            user_params["specific_value"],
            user_params["distance_column"],
            user_params["status_column"],
        )
        orchestrator.run_analysis(distance_targets)
        return redirect(url_for("index"))

    return render_template("config.html", user_params=user_params)


@app.route("/get_points_data")
def get_points_data() -> jsonify:
    """
    Retrieve processed points data as JSON.

    :returns: JSON object with points data, distances, and angles.
    :rtype: Response
    """
    if orchestrator is None:
        return jsonify({"error": "Orchestrator not configured."}), 400
    if len(orchestrator.point_list) == 0:
        return (
            jsonify({"error": "No data available. Please check your configuration."}),
            404,
        )

    dist_angle_map = {}
    for point_id, distance, angle in orchestrator.point_list:
        dist_angle_map.setdefault(distance, []).append(angle)

    for d in dist_angle_map:
        dist_angle_map[d].sort()

    response = {
        "points": [
            {"point_id": pid, "distance": dist, "angle": ang}
            for (pid, dist, ang) in orchestrator.point_list
        ],
        "distances": sorted(dist_angle_map.keys()),
        "angles_per_distance": {str(d): dist_angle_map[d] for d in dist_angle_map},
    }
    return jsonify(response)


@app.route("/get_point_data")
def get_point_data():
    """
    Retrieve specific point data, including metrics and a link to a plot.

    :returns: JSON object containing point metrics and plot URL.
    :rtype: Response
    """
    if orchestrator is None:
        return jsonify({"error": "Orchestrator not configured."}), 400

    point_id = request.args.get("point_id", None)
    if point_id is None:
        return jsonify({"error": "No point_id provided"}), 400

    try:
        point_id = int(point_id)
    except ValueError:
        return jsonify({"error": "Invalid point_id format."}), 400

    matching = [item for item in orchestrator.point_list if item[0] == point_id]
    if not matching:
        return jsonify({"error": "Invalid point_id."}), 404

    _, distance_val, angle_val = matching[0]
    res = orchestrator.results.get((distance_val, angle_val))
    if not res:
        return (
            jsonify(
                {
                    "error": f"No analysis results for distance={distance_val}, angle={angle_val}"
                }
            ),
            404,
        )

    metrics_list, _, _ = res

    # Format metrics table
    metrics_keys = metrics_list[0].keys()
    rows = []
    for metric in metrics_keys:
        row = [metric]
        for m in metrics_list:
            value = m.get(metric, "N/A")
            if isinstance(value, float):
                value = f"{value:.4f}"
            row.append(value)
        rows.append(row)

    headers = ["Metric"] + [f"File {i+1}" for i in range(len(metrics_list))]
    metrics_table = tabulate(rows, headers=headers, tablefmt="grid")

    chart_url = f"/plot_chart?point_id={point_id}"

    return jsonify(
        {
            "title": f"Analysis for Distance={distance_val}cm and Angle={angle_val}°",
            "description": f"Metrics:\n{metrics_table}",
            "chart_url": chart_url,
        }
    )


@app.route("/plot_chart")
def plot_chart():
    """
    Generate and return a chart for a specific point.

    :returns: PNG image of the chart.
    :rtype: Response
    """
    if orchestrator is None:
        return "Orchestrator not configured.", 400

    point_id = int(request.args.get("point_id", 0))
    matching = [item for item in orchestrator.point_list if item[0] == point_id]
    if not matching:
        return "Invalid point_id", 404

    _, distance_val, angle_val = matching[0]
    res = orchestrator.results.get((distance_val, angle_val))
    if not res:
        return "No analysis results for this (distance, angle)", 404

    metrics_list, fig, _ = res
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    plt.close(fig)
    return send_file(img_bytes, mimetype="image/png")


@app.route("/download_pdf")
def download_pdf() -> send_file:
    """
    Generate and return a PDF containing all analysis results.

    :returns: PDF file containing charts and metrics.
    :rtype: Response
    """
    if orchestrator is None or len(orchestrator.point_list) == 0:
        return "No data available to export.", 400

    pdf_bytes = io.BytesIO()
    with PdfPages(pdf_bytes) as pdf:
        for (distance, angle), value in orchestrator.results.items():
            metrics, fig, *_ = value  # Unpack metrics and fig safely

            # Save the figure
            pdf.savefig(fig)
            plt.close(fig)

            # Prepare transposed metrics
            transposed_metrics = defaultdict(list)
            for metric_dict in metrics:
                for key, value in metric_dict.items():
                    transposed_metrics[key].append(f"{value:.4f}" if isinstance(value, float) else value)

            # Create table data
            headers = ["Metric"] + [f"File {i + 1}" for i in range(len(metrics))]
            rows = [[metric] + values for metric, values in transposed_metrics.items()]

            # Generate tabulated output
            metrics_table = tabulate(rows, headers=headers, tablefmt="grid")

            # Increase figure size to fit table
            wrapped_table = textwrap.fill(metrics_table, width=120)  # Wrap long tables
            fig_text = plt.figure(figsize=(12, 14))  # Adjust size
            plt.text(
                0.01,
                0.99,
                f"Analysis for Distance={distance}cm and Angle={angle}°\nMetrics:\n{metrics_table}",
                ha="left",
                va="top",
                fontsize=8,  # Adjust font size for better fit
                family="monospace",
            )
            plt.axis("off")
            pdf.savefig(fig_text)
            plt.close(fig_text)
    pdf_bytes.seek(0)
    return send_file(
        pdf_bytes,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="analysis_results.pdf",
    )



if __name__ == "__main__":
    app.run(debug=True)
