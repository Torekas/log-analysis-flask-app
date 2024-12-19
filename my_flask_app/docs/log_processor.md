Module log_processor
====================

Functions
---------

`create_table_from_csv(csv_file: str, conn: sqlite3.Connection) ‑> None`
:   Create a table and insert data from a CSV file into an SQLite database.
    
    :param str csv_file: Path to the CSV file to be processed.
    :param sqlite3.Connection conn: SQLite database connection object.
    :returns: None
    :rtype: None

`parse_json_blocks(line: str) ‑> Dict | List | None`
:   Parses JSON log blocks within a line.
    
    :param str line: A single line from the log file that may contain JSON data.
    :returns: Parsed JSON data as a dictionary or list, or None if parsing fails.
    :rtype: Optional[Union[Dict, List]]

`parse_session_info_entry(entry_content: str) ‑> Dict[str, str]`
:   Parses a SESSION_INFO_NTF style entry that may contain nested structures.
    
    :param str entry_content: Content of the SESSION_INFO_NTF log entry.
    :returns: A dictionary containing key-value pairs extracted from the log entry.
    :rtype: Dict[str, str]

`process_csv_files(csv_dir: str, db_file: str) ‑> None`
:   Process all CSV files in the directory and create corresponding tables in the database.
    
    :param str csv_dir: Path to the directory containing CSV files.
    :param str db_file: Path to the SQLite database file.
    :returns: None
    :rtype: None

`process_log_file(log_file: str, csv_file: str) ‑> None`
:   Process a log file to extract SESSION_INFO_NTF and JSON data into a CSV file.
    
    :param str log_file: Path to the input log file.
    :param str csv_file: Path to the output CSV file.
    :returns: None
    :rtype: None

`run_log_processing(log_dir: str = './logs', output_dir: str = './output', db_file: str = './logs_data.db') ‑> bool`
:   Run the entire log processing pipeline.
    
    :param str log_dir: Directory containing log files.
    :param str output_dir: Directory where output CSV files will be saved.
    :param str db_file: Path to the SQLite database file.
    :returns: True if processing is successful.
    :rtype: bool