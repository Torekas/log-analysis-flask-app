Module orchestrator
===================

Classes
-------

`Orchestrator(directory: str, specific_value: str, distance_column: str, status_column: str)`
:   Orchestrator class to manage log file analysis, evaluate measurements, and generate visualizations.
    
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
    
    Initialize the Orchestrator class with configuration parameters.
    
    :param directory: Path to the directory containing CSV files.
    :param specific_value: The specific value to filter measurements.
    :param distance_column: Name of the column representing distances.
    :param status_column: Name of the column representing statuses.

    ### Class variables

    `FILE_INDEX_TO_DEGREE`
    :

    ### Static methods

    `compare_metrics(metrics1: Dict[str, float], metrics2: Dict[str, float]) ‑> str`
    :   Compare two sets of metrics and return a formatted table.
        
        :param metrics1: First set of metrics.
        :param metrics2: Second set of metrics.
        :returns: A formatted string containing the comparison table.

    ### Methods

    `analyze_measurements(self, measurements_list: List[List[float]], target_value: int, title_suffix: str = '') ‑> Tuple[List[Dict[str, float]], matplotlib.figure.Figure, List[List[float]]]`
    :   Analyze measurements to compute error metrics and generate visualizations.
        
        :param measurements_list: List of lists containing measurement values.
        :param target_value: Target value for comparison.
        :param title_suffix: Suffix for the plot title.
        :returns: A tuple containing a list of metrics, a plot figure, and errors.

    `concatenate_values(self, distance: int, angle: int) ‑> List[List[float]]`
    :   Extract values filtered by the specific value from all files for a given (distance, angle).
        
        :param distance: Distance value to filter the data.
        :param angle: Angle value to filter the data.
        :returns: A list of lists, each containing filtered measurements for a file.

    `load_csv_files(self) ‑> None`
    :   Load CSV files from the directory and group them by (distance, angle).
        
        :raises FileNotFoundError: If the specified directory does not exist.

    `run_analysis(self, distance_targets: Dict[int, int]) ‑> None`
    :   Run the analysis pipeline: load CSV files, compute metrics, and generate plots.
        
        :param distance_targets: A dictionary mapping distances to their target values.

    `visualize_results(self, measurements_list: List[List[float]], errors_list: List[List[float]], target_value: int, title_suffix: str) ‑> matplotlib.figure.Figure`
    :   Generate visualizations for measurements and errors.
        
        :param measurements_list: List of measurements for each file.
        :param errors_list: List of errors for each file.
        :param target_value: Target value for comparison.
        :param title_suffix: Suffix for the plot title.
        :returns: A matplotlib Figure object containing the plots.