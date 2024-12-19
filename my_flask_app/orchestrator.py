import os
import re

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from tabulate import tabulate


class Orchestrator:
    """
    Orchestrator class to manage log file analysis, evaluate measurements, and generate visualizations.

    Attributes:
        FILE_INDEX_TO_DEGREE (Dict[int, str]): Mapping of file indices to degree labels.
        directory (str): Absolute path to the directory containing CSV files.
        specific_value (str): Specific value to filter measurements in the data.
        distance_column (str): Name of the column representing distances.
        status_column (str): Name of the column representing statuses.
        dataframes (Dict[Tuple[int, int], List[pd.DataFrame]]): Loaded dataframes grouped by (distance, angle).
        results (Dict[Tuple[int, int], Tuple[List[Dict[str, float]], plt.Figure, List[List[float]]]]):
            Results containing metrics, plots, and errors for each (distance, angle).
        point_list (List[Tuple[int, int, int]]): List of (point_id, distance, angle) for processed points.
    """

    FILE_INDEX_TO_DEGREE = {
        1: "0°",
        2: "45°",
        3: "90°",
        4: "135°",
        5: "180°",
        6: "225°",
        7: "270°",
        8: "315°",
    }

    def __init__(
        self,
        directory: str,
        specific_value: str,
        distance_column: str,
        status_column: str,
    ) -> None:
        """
        Initialize the Orchestrator class with configuration parameters.

        :param directory: Path to the directory containing CSV files.
        :param specific_value: The specific value to filter measurements.
        :param distance_column: Name of the column representing distances.
        :param status_column: Name of the column representing statuses.
        """
        self.directory: str = os.path.abspath(directory)
        self.specific_value: str = specific_value
        self.distance_column: str = distance_column
        self.status_column: str = status_column
        self.dataframes: Dict[Tuple[int, int], List[pd.DataFrame]] = {}
        self.results: Dict[
            Tuple[int, int],
            Tuple[List[Dict[str, float]], plt.Figure, List[List[float]]],
        ] = {}
        self.point_list: List[Tuple[int, int, int]] = []
        self.board_type: Optional[str] = None  # "Big" or "Small"

    def load_csv_files(self) -> None:
        """
        Load CSV files from the directory and group them by (distance, angle).

        :raises FileNotFoundError: If the specified directory does not exist.
        """
        current_dir = os.getcwd()
        try:
            os.chdir(self.directory)
            print("Loading CSV files...")
            # Updated pattern to handle "Big", "Small", or "BigSmall" boards and optional index
            pattern = r"Putty_(Big|Small|BigSmall)_(\d+)cm_initf_115200_(\d+)_degree(?:_(\d+))?\.csv"

            for file in os.listdir(self.directory):
                if file.endswith(".csv"):
                    match = re.match(pattern, file)
                    if match:
                        board_type, dist_str, angle_str, file_index_str = match.groups()
                        distance = int(dist_str)
                        angle = int(angle_str)

                        # Store the board_type if not already stored
                        if self.board_type is None:
                            self.board_type = board_type

                        df = pd.read_csv(os.path.join(self.directory, file))
                        self.dataframes.setdefault((distance, angle), []).append(df)
                        print(f"Loaded {file} into dataframes[({distance}, {angle})]")

            print(
                f"Total number of (distance, angle) groups loaded: {len(self.dataframes)}"
            )
        finally:
            os.chdir(current_dir)

    def concatenate_values(self, distance: int, angle: int) -> List[List[float]]:
        """
        Extract values filtered by the specific value from all files for a given (distance, angle).

        :param distance: Distance value to filter the data.
        :param angle: Angle value to filter the data.
        :returns: A list of lists, each containing filtered measurements for a file.
        """
        df_list = self.dataframes.get((distance, angle), [])
        measurements_per_file = []
        for df in df_list:
            vals = df[self.distance_column][
                df[self.status_column].str.lower() == self.specific_value.lower()
                ].tolist()
            measurements_per_file.append(vals)
        return measurements_per_file

    def analyze_measurements(
        self,
        measurements_list: List[List[float]],
        target_value: int,
        title_suffix: str = "",
    ) -> Tuple[List[Dict[str, float]], plt.Figure, List[List[float]]]:
        """
        Analyze measurements to compute error metrics and generate visualizations.

        :param measurements_list: List of lists containing measurement values.
        :param target_value: Target value for comparison.
        :param title_suffix: Suffix for the plot title.
        :returns: A tuple containing a list of metrics, a plot figure, and errors.
        """
        metrics_list = []
        errors_list = []
        for measurements in measurements_list:
            y = np.array(measurements)
            errors = y - target_value
            abs_errors = np.abs(errors)

            metrics = {
                "MAE": np.mean(abs_errors) if len(abs_errors) > 0 else np.nan,
                "MSE": np.mean(errors**2) if len(errors) > 0 else np.nan,
                "RMSE": np.sqrt(np.mean(errors**2)) if len(errors) > 0 else np.nan,
                "MAPE": (
                    np.mean(abs_errors / target_value) * 100
                    if target_value != 0 and len(errors) > 0
                    else None
                ),
                "Max Error": np.max(abs_errors) if len(abs_errors) > 0 else np.nan,
                "Std Error": np.std(errors) if len(errors) > 0 else np.nan,
            }

            metrics_list.append(metrics)
            errors_list.append(errors.tolist())

        fig = self.visualize_results(
            measurements_list, errors_list, target_value, title_suffix
        )
        return metrics_list, fig, errors_list

    def visualize_results(
        self,
        measurements_list: List[List[float]],
        errors_list: List[List[float]],
        target_value: int,
        title_suffix: str,
    ) -> plt.Figure:
        """
        Generate visualizations for measurements and errors.

        :param measurements_list: List of measurements for each file.
        :param errors_list: List of errors for each file.
        :param target_value: Target value for comparison.
        :param title_suffix: Suffix for the plot title.
        :returns: A matplotlib Figure object containing the plots.
        """
        colors = plt.cm.tab10.colors  # Use a colormap with 10 distinct colors
        num_files = len(measurements_list)

        # Ensure we have enough colors
        if num_files > len(colors):
            colors = colors * (num_files // len(colors) + 1)

        degrees = [
            self.FILE_INDEX_TO_DEGREE.get(i + 1, f"File {i + 1}")
            for i in range(num_files)
        ]

        fig = plt.figure(figsize=(16, 12))
        fig.suptitle(
            f"Analysis of Measurements for Goal: {target_value} ({title_suffix})",
            fontsize=16,
            fontweight="bold",
        )

        ax1 = fig.add_subplot(2, 2, 1)
        ax1.hist(
            errors_list, bins=10, color=colors[:num_files], alpha=0.6, edgecolor="black"
        )
        ax1.set_title("Histogram of Errors")
        ax1.legend(title="Degrees", labels=degrees)

        ax2 = fig.add_subplot(2, 2, 2)
        for i, measurements in enumerate(measurements_list):
            ax2.plot(measurements, "o-", label=degrees[i], color=colors[i])
        ax2.axhline(target_value, color="r", linestyle="--", label="Target")
        ax2.set_title("Actual Values vs. Target")
        ax2.legend(title="Degrees")

        ax3 = fig.add_subplot(2, 2, 3)
        for i, errors in enumerate(errors_list):
            ax3.plot(errors, "s-", label=degrees[i], color=colors[i])
        ax3.set_title("Errors")
        ax3.legend(title="Degrees")

        ax4 = fig.add_subplot(2, 2, 4)
        bplot = ax4.boxplot(errors_list, vert=False, patch_artist=True, labels=degrees)
        for i, box in enumerate(bplot["boxes"]):
            box.set_facecolor(colors[i])
        ax4.set_title("Boxplot of Errors per Degree")

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        return fig

    def run_analysis(self, distance_targets: Dict[int, int]) -> None:
        """
        Run the analysis pipeline: load CSV files, compute metrics, and generate plots.

        :param distance_targets: A dictionary mapping distances to their target values.
        """
        self.load_csv_files()
        # Adjust the distance_targets based on board type
        if self.board_type == "Big":
            # For Big boards: 100, 150, 200
            distance_targets = {100: 100, 150: 150, 200: 200}
        elif self.board_type == "Small":
            # For Small boards: 100, 200, 300
            distance_targets = {100: 100, 200: 200, 300: 300}

        all_pairs = sorted(self.dataframes.keys(), key=lambda x: (x[0], x[1]))
        point_id = 1
        for distance, angle in all_pairs:
            # Default to 100 if no target provided
            target_value = distance_targets.get(distance, 100)
            measurements_list = self.concatenate_values(distance, angle)
            if any(len(m) > 0 for m in measurements_list):
                suffix = f"{distance}cm_{angle}degree"
                metrics_list, fig, errors_list = self.analyze_measurements(
                    measurements_list, target_value, suffix
                )
                self.results[(distance, angle)] = (metrics_list, fig, errors_list)
                self.point_list.append((point_id, distance, angle))
                point_id += 1

    @staticmethod
    def compare_metrics(metrics1: Dict[str, float], metrics2: Dict[str, float]) -> str:
        """
        Compare two sets of metrics and return a formatted table.

        :param metrics1: First set of metrics.
        :param metrics2: Second set of metrics.
        :returns: A formatted string containing the comparison table.
        """
        combined = []
        for key in set(metrics1.keys()).union(metrics2.keys()):
            row = [key, metrics1.get(key, "None"), metrics2.get(key, "None")]
            combined.append(row)
        return tabulate(combined, headers=["Metrics", "SET1", "SET2"], tablefmt="grid")
