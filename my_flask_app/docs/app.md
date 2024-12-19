Module app
==========

Functions
---------

`config() ‑> str`
:   Configure user parameters for analysis.
    
    :returns: HTML content for the configuration page.
    :rtype: str

`download_pdf() ‑> <function send_file at 0x000001691468E8E0>`
:   Generate and return a PDF containing all analysis results.
    
    :returns: PDF file containing charts and metrics.
    :rtype: Response

`get_point_data()`
:   Retrieve specific point data, including metrics and a link to a plot.
    
    :returns: JSON object containing point metrics and plot URL.
    :rtype: Response

`get_points_data() ‑> <function jsonify at 0x00000169145AC360>`
:   Retrieve processed points data as JSON.
    
    :returns: JSON object with points data, distances, and angles.
    :rtype: Response

`index() ‑> str`
:   Render the main index page.
    
    :returns: HTML content for the main page.
    :rtype: str

`plot_chart()`
:   Generate and return a chart for a specific point.
    
    :returns: PNG image of the chart.
    :rtype: Response

`process_logs() ‑> str`
:   Process log files into CSV and SQLite database.
    
    :returns: HTML content for the result of log processing.
    :rtype: str